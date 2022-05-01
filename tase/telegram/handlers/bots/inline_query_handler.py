from __future__ import annotations
from collections import defaultdict
from typing import List

import arrow
import emoji
import pyrogram
from pyrogram.types import InlineQueryResultCachedAudio, InlineKeyboardMarkup, InlineKeyboardButton

from tase.db import elasticsearch_models
from tase.my_logger import logger
from tase.telegram.handlers import BaseHandler, HandlerMetadata
from tase.utils import get_timestamp
from pyrogram import handlers


class InlineQueryHandler(BaseHandler):

    def init_handlers(self) -> List[HandlerMetadata]:
        return [
            HandlerMetadata(
                cls=handlers.InlineQueryHandler,
                callback=self.on_inline_query,
            )
        ]

    def on_inline_query(self, client: 'pyrogram.Client', inline_query: 'pyrogram.types.InlineQuery'):
        logger.debug(f"on_inline_query: {inline_query}")
