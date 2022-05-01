from __future__ import annotations

from typing import Dict, List

import kombu
from pydantic import BaseModel

from tase.db.database_client import DatabaseClient
from .handler_metadata import HandlerMetadata
from ...telegram_client import TelegramClient


class BaseHandler(BaseModel):
    db: 'DatabaseClient'
    task_queues: Dict['str', 'kombu.Queue']
    telegram_client: 'TelegramClient'

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List['HandlerMetadata']:
        raise NotImplementedError