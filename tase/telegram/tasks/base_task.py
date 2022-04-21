from dataclasses import dataclass, field
from typing import List, Callable

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient


def exception_handler(func: 'Callable'):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrap


@dataclass
class BaseTask:
    name: str = field(default="")
    args: List[object] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    @exception_handler
    def run_task(self, telegram_client: 'TelegramClient', db: 'DatabaseClient'):
        pass
