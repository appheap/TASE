from typing import Optional, List, Tuple

import pyrogram.types

from tase.my_logger import logger
from . import graph_models, elasticsearch_models, document_models
from .document_db import DocumentDatabase
from .elasticsearch_db import ElasticsearchDatabase
from .graph_db import GraphDatabase
from ..configs import ElasticConfig, ArangoDBConfig


class DatabaseClient:
    _es_db: "ElasticsearchDatabase"
    _graph_db: "GraphDatabase"
    _document_db: "DocumentDatabase"

    def __init__(
        self,
        elasticsearch_config: ElasticConfig,
        arangodb_config: ArangoDBConfig,
    ):

        self._es_db = ElasticsearchDatabase(
            elasticsearch_config=elasticsearch_config,
        )

        self._graph_db = GraphDatabase(
            arangodb_config=arangodb_config,
        )

        self._document_db = DocumentDatabase(
            doc_db_config=arangodb_config,
        )

    def update_user_chosen_language(
        self, user: graph_models.vertices.User, lang_code: str
    ):
        if user is None or lang_code is None:
            return

        self._graph_db.update_user_chosen_language(user, lang_code)

    def get_user_by_user_id(self, user_id: int) -> Optional[graph_models.vertices.User]:
        if user_id is None:
            return None
        return self._graph_db.get_user_by_user_id(user_id)

    def get_or_create_user(
        self, telegram_user: "pyrogram.types.User"
    ) -> Optional[graph_models.vertices.User]:
        if telegram_user is None:
            return None
        return self._graph_db.get_or_create_user(telegram_user)

    def update_or_create_user(
        self, telegram_user: "pyrogram.types.User"
    ) -> Optional[graph_models.vertices.User]:
        if telegram_user is None:
            return None
        return self._graph_db.update_or_create_user(telegram_user)

    def get_or_create_chat(
        self,
        telegram_chat: "pyrogram.types.Chat",
        creator: graph_models.vertices.User = None,
        member: graph_models.vertices.User = None,
    ) -> Optional[graph_models.vertices.Chat]:
        if telegram_chat is None:
            return None
        return self._graph_db.get_or_create_chat(telegram_chat, creator, member)

    def update_or_create_chat(
        self,
        telegram_chat: "pyrogram.types.Chat",
        creator: graph_models.vertices.User = None,
        member: graph_models.vertices.User = None,
    ) -> Optional[graph_models.vertices.Chat]:
        if telegram_chat is None:
            return None
        return self._graph_db.update_or_create_chat(telegram_chat, creator, member)

    def get_or_create_audio(
        self, message: "pyrogram.types.Message", telegram_client_id: int
    ):
        if message is None or message.audio is None:
            return
        try:
            self._es_db.get_or_create_audio(message)
            self._graph_db.get_or_create_audio(message)
            self._document_db.get_or_create_audio(message, telegram_client_id)
        except Exception as e:
            logger.exception(e)

    def update_or_create_audio(
        self, message: "pyrogram.types.Message", telegram_client_id: int
    ):
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
        inline_query: "pyrogram.types.InlineQuery",
        query_date: int,
        query_metadata: dict,
        audio_docs: List[elasticsearch_models.Audio],
        next_offset: Optional[str],
    ) -> Optional[
        Tuple[graph_models.vertices.InlineQuery, List[graph_models.vertices.Hit]]
    ]:
        if (
            bot_id is None
            or inline_query is None
            or query_date is None
            or query_metadata is None
            or audio_docs is None
        ):
            return None

        return self._graph_db.get_or_create_inline_query(
            bot_id,
            inline_query,
            query_date,
            query_metadata,
            audio_docs,
            next_offset,
        )

    def get_or_create_query(
        self,
        bot_id: int,
        from_user: "pyrogram.types.User",
        query: "str",
        query_date: int,
        query_metadata: dict,
        audio_docs: List[elasticsearch_models.Audio],
    ) -> Optional[Tuple[graph_models.vertices.Query, List[graph_models.vertices.Hit]]]:
        if (
            bot_id is None
            or from_user is None
            or query is None
            or query_date is None
            or query_metadata is None
            or audio_docs is None
        ):
            return None

        return self._graph_db.get_or_create_query(
            bot_id, from_user, query, query_date, query_metadata, audio_docs
        )

    def search_audio(
        self, query: str, from_: int = 0, size: int = 50
    ) -> Optional[Tuple[List[graph_models.vertices.Audio], dict]]:
        if query is None or from_ is None or size is None:
            return None

        return self._es_db.search_audio(query, from_, size)

    def get_chat_by_chat_id(self, chat_id: int) -> Optional[graph_models.vertices.Chat]:
        if chat_id is None:
            return None

        return self._graph_db.get_chat_by_chat_id(chat_id)

    def get_audio_file_from_cache(
        self,
        audio: "elasticsearch_models.Audio",
        telegram_client_id: int,
    ) -> Optional[document_models.Audio]:
        if audio is None or telegram_client_id is None:
            return None

        return self._document_db.get_audio_file_from_cache(audio, telegram_client_id)

    def get_audio_doc_by_download_url(
        self, download_url: str
    ) -> Optional[elasticsearch_models.Audio]:
        if download_url is None:
            return None

        return self._es_db.get_audio_by_download_url(download_url)

    def get_audio_doc_by_key(self, key: str) -> Optional[elasticsearch_models.Audio]:
        if key is None:
            return None

        return self._es_db.get_audio_by_id(key)

    def get_or_create_download_from_chosen_inline_query(
        self,
        chosen_inline_result: "pyrogram.types.ChosenInlineResult",
        bot_id: int,
    ) -> Optional["graph_models.vertices.Download"]:
        if chosen_inline_result is None or bot_id is None:
            return None

        return self._graph_db.get_or_create_download_from_chosen_inline_query(
            chosen_inline_result, bot_id
        )

    def get_or_create_download_from_download_url(
        self,
        download_url: str,
        from_user: "graph_models.vertices.User",
        bot_id: int,
    ) -> Optional["graph_models.vertices.Download"]:
        if download_url is None or bot_id is None or from_user is None:
            return None

        return self._graph_db.get_or_create_download_from_download_link(
            download_url, from_user, bot_id
        )

    def get_hit_by_download_url(
        self, download_url: str
    ) -> Optional[graph_models.vertices.Hit]:
        if download_url is None:
            return None

        return self._graph_db.get_hit_by_download_url(download_url)

    def get_audio_from_hit(
        self, hit: graph_models.vertices.Hit
    ) -> Optional[graph_models.vertices.Audio]:
        if hit is None:
            return None

        return self._graph_db.get_audio_from_hit(hit)

    def get_user_download_history(
        self,
        db_from_user: graph_models.vertices.User,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Audio]]:
        if db_from_user is None:
            return None

        return self._graph_db.get_user_download_user_history(
            db_from_user, offset, limit
        )

    def get_user_playlists(
        self,
        db_from_user: graph_models.vertices.User,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Playlist]]:
        if db_from_user is None:
            return None

        return self._graph_db.get_user_playlists(db_from_user, offset, limit)

    def add_audio_to_playlist(
        self, playlist_key: str, hit_download_url: str
    ) -> Tuple[bool, bool]:
        if playlist_key is None or hit_download_url is None:
            return False, False

        return self._graph_db.add_audio_to_playlist(playlist_key, hit_download_url)

    def get_playlist_audios(
        self,
        db_from_user: graph_models.vertices.User,
        playlist_key: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Audio]]:
        if (
            db_from_user is None
            or playlist_key is None
            or offset is None
            or limit is None
        ):
            return None

        return self._graph_db.get_playlist_audios(
            db_from_user, playlist_key, offset, limit
        )

    def get_playlist_by_key(self, key: str) -> Optional[graph_models.vertices.Playlist]:
        if key is None:
            return None

        return self._graph_db.get_playlist_by_key(key)
