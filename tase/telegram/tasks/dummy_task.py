import time

from pydantic import Field

from tase.telegram.client import TelegramClient
from .base_task import BaseTask
from ...db import DatabaseClient
from ...my_logger import logger


class DummyTask(BaseTask):
    name: str = Field(default="dummy_task")

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        logger.info(f"{telegram_client.name}: {self.kwargs}")
        time.sleep(1)
