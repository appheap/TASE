from dataclasses import dataclass, field
from typing import List

from tase.db.database_client import DatabaseClient
from tase.telegram import TelegramClient


@dataclass
class BaseTask:
    name: str = field(default="")
    args: List[object] = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def run_task(self, telegram_client: 'TelegramClient', db: 'DatabaseClient'):
        pass
