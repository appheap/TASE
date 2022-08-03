from typing import Callable, List

from pydantic import BaseModel, Field

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram.telegram_client import TelegramClient


def exception_handler(func: "Callable"):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
            logger.info(f"Task Finished")
        except Exception as e:
            logger.exception(e)

    return wrap


class BaseTask(BaseModel):
    name: str = Field(default="")
    args: List[object] = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)

    def run_task(
        self,
        telegram_client: "TelegramClient",
        db: "DatabaseClient",
    ):
        pass
