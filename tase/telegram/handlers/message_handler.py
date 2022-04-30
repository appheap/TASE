import random
import random
import textwrap
import unicodedata as UD
from datetime import timedelta, datetime
from typing import Dict

import emoji
import kombu
import pyrogram
from pydantic import BaseModel
from pyrogram.enums import ParseMode

from static.emoji import _traffic_light, _checkmark_emoji, _floppy_emoji, _clock_emoji, fruit_list, _search_emoji
from tase.db.database_client import DatabaseClient
from tase.my_logger import logger
from tase.telegram import TelegramClient, ClientTypes
from tase.telegram.globals import client_task
from tase.telegram.tasks.index_audios_task import IndexAudiosTask
from tase.utils import get_timestamp

from .base_handler import BaseHandler


class MessageHandler(BaseHandler):

    def on_message(
            self,
            client: 'pyrogram.Client',
            message: 'pyrogram.types.Message'
    ):
        pass