from kombu.mixins import ConsumerProducerMixin

import tase
from tase.telegram.client.worker_commands import BaseWorkerCommand


class ShutdownCommand(BaseWorkerCommand):
    name = "shutdown_command"

    def run_command(
        self,
        consumer_producer: ConsumerProducerMixin,
        telegram_client: tase.telegram.client.TelegramClient,
        db: tase.db.DatabaseClient,
    ) -> None:
        consumer_producer.should_stop = True
        # todo: add more functionality to this command. for instance, wrap the tasks in queue in a job and schedule
        #  them for the next consumer start/restart.
