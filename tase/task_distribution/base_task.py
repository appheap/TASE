from typing import List, Optional

import kombu
from decouple import config
from kombu.entity import TRANSIENT_DELIVERY_MODE
from kombu.mixins import ConsumerProducerMixin, logger
from pydantic import BaseModel, Field

from tase.db import DatabaseClient
from .task_type import TaskType
from .. import task_globals


class BaseTask(BaseModel):
    name: Optional[str] = Field(default=None)
    type: TaskType = Field(default=TaskType.UNKNOWN)

    args: List[object] = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)

    def publish(
        self,
        target_queue: kombu.Queue = None,
        priority: int = 1,
    ) -> bool:
        published = True

        try:
            if self.type == TaskType.UNKNOWN:
                published = False
            elif self.type == TaskType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK:
                self._publish_task(
                    task_globals.telegram_workers_general_task_queue,
                    task_globals.telegram_client_worker_exchange,
                    priority,
                )
            elif self.type == TaskType.ONE_TELEGRAM_CLIENT_CONSUMER_WORK:
                self._publish_task(
                    target_queue,
                    task_globals.telegram_client_worker_exchange,
                    priority,
                )
            elif self.type == TaskType.RABBITMQ_CONSUMER_COMMAND:
                self._publish_task(
                    None,
                    task_globals.rabbitmq_worker_command_exchange,
                    priority,
                )
            elif self.type == TaskType.SCHEDULER_JOB:
                self._publish_task(
                    task_globals.scheduler_queue,
                    task_globals.scheduler_exchange,
                    priority,
                )
            else:
                published = False
        except Exception as e:
            logger.exception(e)
            published = False

        return published

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
