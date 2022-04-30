from collections import defaultdict
from typing import List

import arrow
import emoji
import pyrogram
from pyrogram.types import InlineQueryResultCachedAudio, InlineKeyboardMarkup, InlineKeyboardButton

from .base_handler import BaseHandler
from ...db import elasticsearch_models
from ...my_logger import logger
from ...utils import get_timestamp


class InlineQueryHandler(BaseHandler):

    def on_inline_query(self, client: 'pyrogram.Client', inline_query: 'pyrogram.types.InlineQuery'):
        logger.info(f"on_inline_query: {inline_query}")
