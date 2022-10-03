import time

from kombu.mixins import ConsumerProducerMixin
from pydantic import Field

from tase.db import DatabaseClient
from tase.my_logger import logger
from tase.task_distribution import BaseTask
from tase.telegram.client import TelegramClient


class DummyTask(BaseTask):
    name: str = Field(default="dummy_task")

    def run_task(
        self,
        consumer_producer: ConsumerProducerMixin,
        telegram_client: TelegramClient,
        db: DatabaseClient,
    ):
        logger.info(f"Running Dummy Task with client: {telegram_client.name}")
        time.sleep(5)
        logger.info(f"Finished Dummy Task with client: {telegram_client.name}")
