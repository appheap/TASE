from typing import Optional, List, Tuple

import pyrogram.types

from tase.my_logger import logger
from . import document_models, elasticsearch_models, graph_models
from .document_db import DocumentDatabase
from .elasticsearch_db import ElasticsearchDatabase
from .graph_db import GraphDatabase


class DatabaseClient:
    _es_db: 'ElasticsearchDatabase'
    _graph_db: 'GraphDatabase'
    _document_db: 'DocumentDatabase'

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

        self._document_db = DocumentDatabase(
            doc_db_config=graph_db_config,
        )

    def get_user_by_user_id(self, user_id: int) -> Optional[graph_models.User]:
        if user_id is None:
            return None
        return self._graph_db.get_user_by_user_id(user_id)

    def get_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional[graph_models.User]:
        if telegram_user is None:
            return None
        return self._graph_db.get_or_create_user(telegram_user)

    def update_or_create_user(self, telegram_user: 'pyrogram.types.User') -> Optional[graph_models.User]:
        if telegram_user is None:
            return None
        return self._graph_db.update_or_create_user(telegram_user)

    def get_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: graph_models.User = None,
            member: graph_models.User = None
    ) -> Optional[graph_models.Chat]:
        if telegram_chat is None:
            return None
        return self._graph_db.get_or_create_chat(telegram_chat, creator, member)

    def update_or_create_chat(
            self,
            telegram_chat: 'pyrogram.types.Chat',
            creator: graph_models.User = None,
            member: graph_models.User = None
    ) -> Optional[graph_models.Chat]:
        if telegram_chat is None:
            return None
        return self._graph_db.update_or_create_chat(telegram_chat, creator, member)

    def get_or_create_audio(self, message: 'pyrogram.types.Message', telegram_client_id: int):
        if message is None or message.audio is None:
            return
        try:
            self._es_db.get_or_create_audio(message)
            self._graph_db.get_or_create_audio(message)
            self._document_db.get_or_create_audio(message, telegram_client_id)
        except Exception as e:
            logger.exception(e)

    def update_or_create_audio(self, message: 'pyrogram.types.Message', telegram_client_id: int):
        if message is None or message.audio is None or telegram_client_id is None:
            return
        try:
            self._es_db.update_or_create_audio(message)
            self._graph_db.update_or_create_audio(message)
            self._document_db.update_or_create_audio(message, telegram_client_id)
        except Exception as e:
            logger.exception(e)

    def get_or_create_inline_query(
            self,
            bot_id: int,
            inline_query: 'pyrogram.types.InlineQuery',
            query_date: int,
            query_metadata: dict,
            audio_docs: List[elasticsearch_models.Audio]
    ) -> Optional[graph_models.InlineQuery]:
        if bot_id is None or inline_query is None or query_date is None or query_metadata is None or audio_docs is None:
            return None

        return self._graph_db.get_or_create_inline_query(bot_id, inline_query, query_date, query_metadata, audio_docs)

    def get_or_create_query(
            self,
            bot_id: int,
            from_user: 'pyrogram.types.User',
            query: 'str',
            query_date: int,
            query_metadata: dict,
            audio_docs: List[elasticsearch_models.Audio]
    ) -> Optional[graph_models.Query]:
        if bot_id is None or from_user is None or query is None or query_date is None or query_metadata is None or audio_docs is None:
            return None

        return self._graph_db.get_or_create_query(bot_id, from_user, query, query_date, query_metadata, audio_docs)

    def search_audio(
            self,
            query: str,
            from_: int = 0,
            size: int = 50
    ) -> Optional[Tuple[List[graph_models.Audio], dict]]:
        if query is None or from_ is None or size is None:
            return None

        return self._es_db.search_audio(query, from_, size)

    def get_chat_by_chat_id(self, chat_id: int) -> Optional[graph_models.Chat]:
        if chat_id is None:
            return None

        return self._graph_db.get_chat_by_chat_id(chat_id)

    def get_audio_file_from_cache(
            self,
            audio: 'elasticsearch_models.Audio',
            telegram_client_id: int,
    ) -> Optional[document_models.Audio]:
        if audio is None or telegram_client_id is None:
            return None

        return self._document_db.get_audio_file_from_cache(audio, telegram_client_id)

    def get_audio_doc_by_download_url(self, download_url: str) -> Optional[elasticsearch_models.Audio]:
        if download_url is None:
            return None

        return self._es_db.get_audio_by_download_url(download_url)
