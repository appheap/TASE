from kombu.mixins import ConsumerProducerMixin

from tase.db import DatabaseClient
from tase.telegram.client import TelegramClient
from .base_task import BaseTask
from .target_worker_type import TargetWorkerType
from ..db.arangodb.enums import RabbitMQTaskType


class ShutdownTask(BaseTask):
    target_worker_type = TargetWorkerType.RABBITMQ_CONSUMER_COMMAND
    type = RabbitMQTaskType.SHUTDOWN_TASK

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        self.task_in_worker(db)
        consumer_producer.should_stop = True
        # todo: add more functionality to this command. for instance, wrap the tasks in queue in a job and schedule
        #  them for the next consumer start/restart.
        self.task_done(db)
