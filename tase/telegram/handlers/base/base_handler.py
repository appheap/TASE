from __future__ import annotations

from typing import Dict, List, Callable

import kombu
from pydantic import BaseModel

from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.templates import QueryResultsTemplate, NoResultsWereFoundTemplate, AudioCaptionTemplate
from .handler_metadata import HandlerMetadata
from ...telegram_client import TelegramClient


def exception_handler(func: 'Callable'):
    def wrap(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)

    return wrap


class BaseHandler(BaseModel):
    db: 'DatabaseClient'
    task_queues: Dict['str', 'kombu.Queue']
    telegram_client: 'TelegramClient'

    query_results_template: QueryResultsTemplate = QueryResultsTemplate()
    no_results_were_found_template: NoResultsWereFoundTemplate = NoResultsWereFoundTemplate()
    audio_caption_template: AudioCaptionTemplate = AudioCaptionTemplate()

    class Config:
        arbitrary_types_allowed = True

    def init_handlers(self) -> List['HandlerMetadata']:
        raise NotImplementedError
