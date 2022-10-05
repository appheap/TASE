from typing import List, Optional, Tuple

import kombu
from decouple import config
from kombu.entity import TRANSIENT_DELIVERY_MODE
from kombu.mixins import ConsumerProducerMixin
from pydantic import BaseModel, Field

from tase.db import DatabaseClient
from .target_worker_type import TargetWorkerType
from .. import task_globals
from ..db.arangodb.enums import RabbitMQTaskType, RabbitMQTaskStatus
from ..my_logger import logger


class BaseTask(BaseModel):
    target_worker_type: TargetWorkerType = Field(default=TargetWorkerType.UNKNOWN)
    type: RabbitMQTaskType = Field(default=RabbitMQTaskType.UNKNOWN)

    kwargs: dict = Field(default_factory=dict)

    task_key: Optional[str]

    def publish(
        self,
        db: DatabaseClient,
        target_queue: kombu.Queue = None,
        priority: int = 1,
    ) -> Tuple[Optional[RabbitMQTaskStatus], bool]:
        if self.target_worker_type == TargetWorkerType.UNKNOWN:
            return None, False

        state_dict = self.kwargs if len(self.kwargs) else None
        active_task = db.document.get_active_rabbitmq_task(
            self.type,
            state_dict,
        )
        status = None
        created = False
        if active_task is None:
            new_task = db.document.create_rabbitmq_task(
                self.type,
                state_dict,
            )
            if new_task:
                self.task_key = new_task.key

            try:
                if (
                    self.target_worker_type
                    == TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
                ):
                    self._publish_task(
                        task_globals.telegram_workers_general_task_queue,
                        task_globals.telegram_client_worker_exchange,
                        priority,
                    )
                elif (
                    self.target_worker_type
                    == TargetWorkerType.ONE_TELEGRAM_CLIENT_CONSUMER_WORK
                ):
                    self._publish_task(
                        target_queue,
                        task_globals.telegram_client_worker_exchange,
                        priority,
                    )
                elif (
                    self.target_worker_type
                    == TargetWorkerType.RABBITMQ_CONSUMER_COMMAND
                ):
                    self._publish_task(
                        None,
                        task_globals.rabbitmq_worker_command_exchange,
                        priority,
                    )
                elif self.target_worker_type == TargetWorkerType.SCHEDULER_JOB:
                    self._publish_task(
                        task_globals.scheduler_queue,
                        task_globals.scheduler_exchange,
                        priority,
                    )
            except Exception as e:
                logger.exception(e)
                new_task.update_status(RabbitMQTaskStatus.FAILED)
            else:
                new_task.update_status(RabbitMQTaskStatus.IN_QUEUE)

            status = new_task.status
            created = True

        else:
            status = active_task.status
            created = False

        return status, created

    def _publish_task(
        self,
        target_queue: kombu.Queue = None,
        exchange: kombu.Exchange = None,
        priority: int = 1,
    ):
        """
        Publishes an object on a queue to be processed

        Parameters
        ----------
        target_queue : kombu.Queue
            Queue to send the body to
        exchange : kombu.Exchange
            Exchange to send the body to
        priority : int, default : 1
            Priority of this task on the queue
        """
        if exchange is None:
            raise Exception("Parameter `exchange` cannot be `None`")

        routing_key = ""
        if exchange and target_queue:
            routing_key = target_queue.routing_key

        declare = [target_queue] if target_queue else []

        with kombu.Connection(
            config("RABBITMQ_URL"),
            userid=config("RABBITMQ_DEFAULT_USER"),
            password=config("RABBITMQ_DEFAULT_PASS"),
        ) as conn:
            producer = conn.Producer(serializer="pickle")
            producer.publish(
                body=self,
                delivery_mode=TRANSIENT_DELIVERY_MODE,
                exchange=exchange,
                routing_key=routing_key,
                declare=declare,
                retry=True,
                priority=priority,
                retry_policy={
                    "interval_start": 0,
                    "interval_step": 2,
                    "interval_max": 30,
                    "max_retries": 30,
                },
            )

    def run(
        self,
        consumer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: "TelegramClient" = None,
    ):
        raise NotImplementedError

    def task_in_worker(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.IN_WORKER)

        return False

    def task_done(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.DONE)

        return False

    def task_failed(
        self,
        db: DatabaseClient,
    ) -> bool:
        task = db.document.get_rabbitmq_task_by_key(self.task_key)
        if task:
            return task.update_status(RabbitMQTaskStatus.FAILED)

        return False
