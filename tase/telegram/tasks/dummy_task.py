import time

from pydantic import Field

from .base_task import BaseTask, exception_handler
from ..telegram_client import TelegramClient
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
