from kombu.mixins import ConsumerProducerMixin

from tase.db import DatabaseClient
from tase.task_distribution import BaseTask
from tase.telegram.client import TelegramClient


class ShutdownTask(BaseTask):
    name = "shutdown_task"

    def run_task(
        self,
        consumer_producer: ConsumerProducerMixin,
        telegram_client: TelegramClient,
        db: DatabaseClient,
    ) -> None:
        consumer_producer.should_stop = True
        # todo: add more functionality to this command. for instance, wrap the tasks in queue in a job and schedule
        #  them for the next consumer start/restart.
