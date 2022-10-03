from multiprocessing import Process
from typing import List

import kombu
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from kombu import Connection, Consumer, Queue
from kombu.mixins import ConsumerProducerMixin
from kombu.transport import pyamqp

from tase import task_globals
from tase.common.utils import exception_handler
from tase.db import DatabaseClient
from tase.my_logger import logger
from tase.scheduler.jobs import BaseJob
from tase.task_distribution import BaseTask


class SchedulerWorkerProcess(Process):
    def __init__(
        self,
        db: DatabaseClient,
    ):
        super().__init__()

        self.daemon = True
        self.name = "SchedulerWorkerProcess"
        self.db = db
        self.consumer = None

    def run(self) -> None:
        logger.info("SchedulerWorkerProcess started ....")
        self.consumer = SchedulerJobConsumer(
            connection=Connection(
                config("RABBITMQ_URL"),
                userid=config("RABBITMQ_DEFAULT_USER"),
                password=config("RABBITMQ_DEFAULT_PASS"),
            ),
            db=self.db,
        )
        self.consumer.run()


class SchedulerJobConsumer(ConsumerProducerMixin):
    def __init__(
        self,
        connection: kombu.Connection,
        db: DatabaseClient,
    ):
        logger.info("scheduler task consumer started...")
        self.connection = connection
        self.db = db

        self.scheduler_queue = task_globals.scheduler_queue

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

        rabbitmq_worker_command_queue = Queue(
            "scheduler_command_queue",
            exchange=task_globals.rabbitmq_worker_command_exchange,
            routing_key="scheduler_command_queue",
            auto_delete=True,
        )
        self.rabbitmq_worker_command_queue = rabbitmq_worker_command_queue

    def get_consumers(
        self,
        consumer,
        channel,
    ) -> List[Consumer]:
        return [
            Consumer(
                queues=[self.rabbitmq_worker_command_queue],
                callbacks=[self.on_job],
                channel=channel,
                prefetch_count=1,
                accept=["pickle"],
            ),
            Consumer(
                queues=[self.scheduler_queue],
                callbacks=[self.on_job_scheduled],
                channel=channel,
                prefetch_count=1,
                accept=["pickle"],
            ),
        ]

    @exception_handler
    def on_job(
        self,
        body: object,
        message: pyamqp.Message,
    ):
        message.ack()

        if isinstance(body, (BaseJob, BaseTask)):
            logger.info(f"Scheduler got a new task: {body.name}")
            if body.name:
                body.run(self, self.db)
        else:
            # todo: unknown type for body detected, what now?
            raise TypeError(f"Unknown type for `body`: {type(body)}")

    @exception_handler
    def job_runner(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        This method serves as a workaround for BaseJob derivative classes to be run

        Parameters
        ----------
        args : tuple
            A list of arguments provided as input to the job. The first argument is a subclass of
            `BaseJob<tase.telegram.jobs.BaseJob>`
        kwargs : dict
            A dictionary containing other keyword arguments passed to this function.

        Returns
        -------
        None
        """
        args[0].run(self, self.db)

    @exception_handler
    def on_job_scheduled(
        self,
        body: object,
        message: pyamqp.Message,
    ) -> None:
        """
        This method is executed when a new Job is fetched from RabbitMQ exchange and schedules the job on the
        global scheduler

        Parameters
        ----------
        body : tase.telegram.jobs.BaseJob
            Job to be scheduled
        message : pyamqp.Message
            Object containing information about this message
        """
        message.ack()

        from tase.scheduler.jobs import BaseJob

        job: BaseJob = body
        logger.info(f"scheduler_task_consumer_on_job : {job.name}")

        if job.name:
            self.scheduler.add_job(
                self.job_runner,
                trigger=job.trigger,
                args=[
                    job,
                ],
            )
