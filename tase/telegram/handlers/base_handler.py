from typing import Dict

import kombu
from pydantic import BaseModel

from tase.db.database_client import DatabaseClient
from tase.telegram import TelegramClient


class BaseHandler(BaseModel):
    db: 'DatabaseClient'
    task_queues: Dict['str', 'kombu.Queue']
    telegram_client: 'TelegramClient'

    class Config:
        arbitrary_types_allowed = True
