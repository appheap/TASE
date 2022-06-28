import time
from dataclasses import dataclass, field

from .base_task import BaseTask, exception_handler
from ..telegram_client import TelegramClient
from ...db import DatabaseClient
from ...my_logger import logger


@dataclass
class DummyTask(BaseTask):
    name: str = field(default="dummy_task")

    @exception_handler
    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        logger.info(f"{telegram_client.name}: {self.kwargs}")
        time.sleep(1)
