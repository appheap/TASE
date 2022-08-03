from multiprocessing import Process
from typing import Dict, List

import kombu
from apscheduler.schedulers.background import BackgroundScheduler
from decouple import config
from kombu import Connection, Consumer
from kombu.mixins import ConsumerProducerMixin
from kombu.transport import pyamqp

import tase
from tase.my_logger import logger
from tase.telegram.globals import scheduler_queue
from tase.telegram.jobs import BaseJob
from tase.telegram.jobs.base_job import exception_handler


class SchedulerWorkerProcess(Process):
    def __init__(
        self,
        index: int,
        db: "tase.db.DatabaseClient",
        task_queues: Dict["str", "kombu.Queue"],
    ):
        super().__init__()
        self.daemon = True
        self.name = f"SchedulerWorkerProcess {index}"
        self.index = index
        self.db = db
        self.task_queues = task_queues
        self.consumer = None

    def run(self) -> None:
        logger.info(f"SchedulerWorkerProcess {self.index} started ....")
        self.consumer = SchedulerTaskConsumer(
            connection=Connection(
                config("RABBITMQ_URL"),
                userid=config("RABBITMQ_DEFAULT_USER"),
                password=config("RABBITMQ_DEFAULT_PASS"),
            ),
            db=self.db,
            task_queues=self.task_queues,
        )
        self.consumer.run()


class SchedulerTaskConsumer(ConsumerProducerMixin):
    def __init__(
        self,
        connection: "Connection",
        db,
        task_queues: Dict["str", "kombu.Queue"],
    ):
        logger.info("scheduler task consumer started...")
        self.connection = connection
        self.db = db
        self.task_queues = task_queues

        self.scheduler_queue = scheduler_queue

        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def get_consumers(
        self,
        consumer,
        channel,
    ) -> List[Consumer]:
        return [
            Consumer(
                queues=[self.scheduler_queue],
                callbacks=[self.on_job_scheduled],
                channel=channel,
                prefetch_count=1,
                accept=["pickle"],
            ),
        ]

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
        args[0].run_job(self.db)

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
