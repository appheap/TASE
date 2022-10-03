from kombu.mixins import ConsumerProducerMixin

from tase.db import DatabaseClient
from tase.telegram.client import TelegramClient
from .base_task import BaseTask
from .task_type import TaskType


class ShutdownTask(BaseTask):
    name = "shutdown_task"
    type = TaskType.RABBITMQ_CONSUMER_COMMAND

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ) -> None:
        consumer_producer.should_stop = True
        # todo: add more functionality to this command. for instance, wrap the tasks in queue in a job and schedule
        #  them for the next consumer start/restart.
