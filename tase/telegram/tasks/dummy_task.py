import time

from kombu.mixins import ConsumerProducerMixin
from pydantic import Field

from tase.db import DatabaseClient
from tase.db.arangodb.enums import RabbitMQTaskType
from tase.my_logger import logger
from tase.task_distribution import BaseTask, TargetWorkerType
from tase.telegram.client import TelegramClient


class DummyTask(BaseTask):
    target_worker_type = TargetWorkerType.ANY_TELEGRAM_CLIENTS_CONSUMER_WORK
    type = RabbitMQTaskType.DUMMY_TASK

    def run(
        self,
        consumer_producer: ConsumerProducerMixin,
        db: DatabaseClient,
        telegram_client: TelegramClient = None,
    ):
        logger.info(f"Running Dummy Task with client: {telegram_client.name}")
        time.sleep(5)
        logger.info(f"Finished Dummy Task with client: {telegram_client.name}")
