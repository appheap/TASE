from typing import Optional

import pyrogram.types

from tase.db.graph_models.vertices import User, Chat, Audio, InlineQuery
from tase.my_logger import logger
from .elasticsearch_db import ElasticsearchDatabase
from .graph_db import GraphDatabase


class DatabaseClient:
    _es_db: 'ElasticsearchDatabase'
    _graph_db: 'GraphDatabase'

    def __init__(
            self,
            elasticsearch_config: dict,
            graph_db_config: dict,
    ):

        self._es_db = ElasticsearchDatabase(
            elasticsearch_config=elasticsearch_config,
        )

        self._graph_db = GraphDatabase(
            graph_db_config=graph_db_config,
        )

    def get_user_by_user_id(self, user_id: int) -> Optional['User']:
        if user_id is None:
            return None
        return self._graph_db.get_user_by_user_id(user_id)

    def get_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None
        return self._graph_db.get_or_create_user(telegram_user)

    def update_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional['User']:
        if telegram_user is None:
            return None
        return self._graph_db.update_or_create_user(telegram_user)

    def get_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None
        return self._graph_db.get_or_create_chat(telegram_chat, creator, member)

    def update_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: 'User' = None,
            member: 'User' = None
    ) -> Optional['Chat']:
        if telegram_chat is None:
            return None
        return self._graph_db.update_or_create_chat(telegram_chat, creator, member)

    def get_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return
        try:
            self._es_db.get_or_create_audio(message)
            self._graph_db.get_or_create_audio(message)
        except Exception as e:
            logger.exception(e)

    def update_or_create_audio(self, message: 'pyrogram.types.Message') -> Optional['Audio']:
        if message is None or message.audio is None:
            return
        try:
            self._es_db.update_or_create_audio(message)
            self._graph_db.update_or_create_audio(message)
        except Exception as e:
            logger.exception(e)

    def get_or_create_inline_query(
            self,
            bot_id: int,
            inline_query: 'pyrogram.types.InlineQuery'
    ) -> Optional['InlineQuery']:
        if bot_id is None or inline_query is None:
            return None

        return self._graph_db.get_or_create_inline_query(bot_id, inline_query)
