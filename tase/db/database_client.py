from typing import List, Optional, Tuple

import pyrogram.types

from tase.my_logger import logger
from . import document_models, elasticsearch_models, graph_models
from .document_db import DocumentDatabase
from .elasticsearch_db import ElasticsearchDatabase
from .graph_db import GraphDatabase
from ..configs import ArangoDBConfig, ElasticConfig


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
        self,
        user: graph_models.vertices.User,
        lang_code: str,
    ):
        if user is None or lang_code is None:
            return

        self._graph_db.update_user_chosen_language(user, lang_code)

    def get_user_by_user_id(
        self,
        user_id: int,
    ) -> Optional[graph_models.vertices.User]:
        if user_id is None:
            return None
        return self._graph_db.get_user_by_user_id(user_id)

    def get_or_create_user(
        self,
        telegram_user: "pyrogram.types.User",
    ) -> Optional[graph_models.vertices.User]:
        if telegram_user is None:
            return None
        return self._graph_db.get_or_create_user(telegram_user)

    def update_or_create_user(
        self,
        telegram_user: "pyrogram.types.User",
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
        self,
        message: "pyrogram.types.Message",
        telegram_client_id: int,
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
        self,
        message: "pyrogram.types.Message",
        telegram_client_id: int,
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
        inline_query_type: graph_models.vertices.InlineQueryType,
        query_date: int,
        query_metadata: dict,
        audio_docs: List[elasticsearch_models.Audio],
        db_audios: List[graph_models.vertices.Audio],
        next_offset: Optional[str],
    ) -> Tuple[Optional[graph_models.vertices.InlineQuery], Optional[List[graph_models.vertices.Hit]],]:

        return self._graph_db.get_or_create_inline_query(
            bot_id,
            inline_query,
            inline_query_type,
            query_date,
            query_metadata,
            audio_docs,
            db_audios,
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
        db_audios: List[graph_models.vertices.Audio],
    ) -> Optional[Tuple[graph_models.vertices.Query, List[graph_models.vertices.Hit]]]:
        if (
            bot_id is None
            or from_user is None
            or query is None
            or query_date is None
            or query_metadata is None
            or audio_docs is None
            or db_audios is None
        ):
            return None

        return self._graph_db.get_or_create_query(
            bot_id,
            from_user,
            query,
            query_date,
            query_metadata,
            audio_docs,
            db_audios,
        )

    def search_audio(
        self,
        query: str,
        from_: int = 0,
        size: int = 50,
    ) -> Optional[Tuple[List[graph_models.vertices.Audio], dict]]:
        if query is None or from_ is None or size is None:
            return None

        return self._es_db.search_audio(
            query,
            from_,
            size,
        )

    def get_chat_by_chat_id(
        self,
        chat_id: int,
    ) -> Optional[graph_models.vertices.Chat]:
        if chat_id is None:
            return None

        return self._graph_db.get_chat_by_chat_id(chat_id)

    def get_chat_by_username(
        self,
        username: str,
    ) -> Optional[graph_models.vertices.Chat]:
        if username is None:
            return None

        return self._graph_db.get_chat_by_username(username.lower())

    def get_audio_file_from_cache(
        self,
        audio: "elasticsearch_models.Audio",
        telegram_client_id: int,
    ) -> Optional[document_models.Audio]:
        if audio is None or telegram_client_id is None:
            return None

        return self._document_db.get_audio_file_from_cache(audio, telegram_client_id)

    def get_audio_doc_by_download_url(
        self,
        download_url: str,
    ) -> Optional[elasticsearch_models.Audio]:
        if download_url is None:
            return None

        return self._es_db.get_audio_by_download_url(download_url)

    def get_audio_doc_by_key(
        self,
        key: str,
    ) -> Optional[elasticsearch_models.Audio]:
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

        return self._graph_db.get_or_create_download_from_chosen_inline_query(chosen_inline_result, bot_id)

    def get_or_create_download_from_hit_download_url(
        self,
        download_url: str,
        from_user: "graph_models.vertices.User",
        bot_id: int,
    ) -> Optional["graph_models.vertices.Download"]:
        if download_url is None or bot_id is None or from_user is None:
            return None

        return self._graph_db.get_or_create_download_from_hit_download_url(download_url, from_user, bot_id)

    def get_hit_by_download_url(
        self,
        download_url: str,
    ) -> Optional[graph_models.vertices.Hit]:
        if download_url is None:
            return None

        return self._graph_db.get_hit_by_download_url(download_url)

    def get_audio_from_hit(
        self,
        hit: graph_models.vertices.Hit,
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

        return self._graph_db.get_user_download_user_history(db_from_user, offset, limit)

    def get_user_playlists(
        self,
        db_from_user: graph_models.vertices.User,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Playlist]]:
        return self._graph_db.get_user_playlists(db_from_user, offset, limit)

    def remove_audio_from_playlist(
        self,
        playlist_key: str,
        audio_download_url: str,
        deleted_at: int,
    ) -> bool:
        return self._graph_db.remove_audio_from_playlist(
            playlist_key,
            audio_download_url,
            deleted_at,
        )

    def add_audio_to_playlist(
        self,
        playlist_key: str,
        audio_download_url: str,
    ) -> Tuple[bool, bool]:
        return self._graph_db.add_audio_to_playlist(playlist_key, audio_download_url)

    def get_playlist_audios(
        self,
        db_from_user: graph_models.vertices.User,
        playlist_key: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Audio]]:
        return self._graph_db.get_playlist_audios(db_from_user, playlist_key, offset, limit)

    def get_audio_playlists(
        self,
        db_from_user: graph_models.vertices.User,
        audio_download_url: str,
        offset: int = 0,
        limit: int = 20,
    ) -> Optional[List[graph_models.vertices.Playlist]]:
        return self._graph_db.get_audio_playlists(
            db_from_user,
            audio_download_url,
            offset,
            limit,
        )

    def get_playlist_by_key(
        self,
        key: str,
    ) -> Optional[graph_models.vertices.Playlist]:
        if key is None:
            return None

        return self._graph_db.get_playlist_by_key(key)

    def get_audios_from_keys(
        self,
        audio_keys: List[str],
    ) -> Optional[List[graph_models.vertices.Audio]]:
        if audio_keys is None or not len(audio_keys):
            return None

        return self._graph_db.get_audios_from_keys(audio_keys)

    def create_bot_task(
        self,
        user_id: int,
        bot_id: int,
        task_type: "document_models.BotTaskType",
        state_dict: dict = None,
        cancel_recent_task: bool = True,
    ) -> Optional[Tuple[document_models.BotTask, bool]]:
        if cancel_recent_task:
            self._document_db.cancel_recent_bot_task(
                user_id,
                bot_id,
                task_type,
            )
        return self._document_db.create_bot_task(
            user_id,
            bot_id,
            task_type,
            state_dict,
        )

    def update_task_state_dict(
        self,
        user_id: int,
        bot_id: int,
        task_type: "document_models.BotTaskType",
        new_task_state: dict,
    ):
        return self._document_db.update_task_state_dict(user_id, bot_id, task_type, new_task_state)

    def get_latest_bot_task(self, user_id: int, bot_id: int) -> Optional[document_models.BotTask]:
        return self._document_db.get_latest_bot_task(user_id, bot_id)

    def create_playlist(
        self,
        db_user: "graph_models.vertices.User",
        title: str,
        description: str = None,
        is_favorite: bool = False,
    ) -> Optional[Tuple["graph_models.vertices.Playlist", bool]]:
        return self._graph_db.create_playlist(
            db_user,
            title,
            description,
            is_favorite,
        )

    def update_playlist_title(
        self,
        playlist_key: str,
        title: str,
    ):
        return self._graph_db.update_playlist_title(
            playlist_key,
            title,
        )

    def update_playlist_description(
        self,
        playlist_key: str,
        description: str,
    ):
        return self._graph_db.update_playlist_description(
            playlist_key,
            description,
        )

    def delete_playlist(
        self,
        db_from_user: graph_models.vertices.User,
        playlist_key: str,
        deleted_at: int,
    ):
        return self._graph_db.delete_playlist(
            db_from_user,
            playlist_key,
            deleted_at,
        )

    def get_chats_sorted_by_audio_indexer_score(
        self,
    ) -> List[graph_models.vertices.Chat]:
        """
        Gets the list of chats sorted by their audio importance score in a descending order

        Returns
        -------
        A list of Chat objects
        """
        return self._graph_db.get_chats_sorted_by_audio_indexer_score()

    def get_chats_sorted_by_username_extractor_score(
        self,
    ) -> List[graph_models.vertices.Chat]:
        """
        Gets the list of chats sorted by their username extractor importance score in a descending order

        Returns
        -------
        A list of Chat objects
        """
        return self._graph_db.get_chats_sorted_by_username_extractor_score()

    def get_chat_buffer_from_chat(
        self,
        chat: pyrogram.types.Chat,
    ) -> Optional[document_models.ChatBuffer]:
        """
        Get a ChatBuffer by key from the provided Chat

        Parameters
        ----------
        chat : pyrogram.types.Chat
            Chat to get the from

        Returns
        -------
        A ChatBuffer if it exists otherwise returns None
        """
        return self._document_db.get_chat_buffer_from_chat(chat)

    def get_chat_username_buffer_from_chat(
        self,
        username: str,
    ) -> Optional[document_models.ChatUsernameBuffer]:
        """
        Get a ChatUsernameBuffer by the key from the provided username

        Parameters
        ----------
        username : str
            username to get the key from

        Returns
        -------
        A ChatUsernameBuffer if it exists otherwise returns None
        """
        return self._document_db.get_chat_username_buffer_from_chat(username)

    def get_or_create_chat_username_buffer(
        self, username: str
    ) -> Tuple[Optional[document_models.ChatUsernameBuffer], bool]:
        return self._document_db.get_or_create_chat_username_buffer(username)

    def update_username_extractor_metadata(
        self,
        chat: graph_models.vertices.Chat,
        offset_id: int,
        offset_date: int,
    ) -> bool:
        """
        Updates username extractor  offset attributes of the chat after being indexed

        Parameters
        ----------
        chat : Chat
            Chat to update its metadata
        offset_id : int
            New offset id
        offset_date : int
            New offset date (it's a timestamp)

        Returns
        -------
        Whether the update was successful or not
        """
        return self._graph_db.update_username_extractor_metadata(
            chat,
            offset_id,
            offset_date,
        )

    def update_audio_indexer_metadata(
        self,
        chat: graph_models.vertices.Chat,
        offset_id: int,
        offset_date: int,
    ) -> bool:
        """
        Updates audio indexer offset attributes of the chat after being indexed

        Parameters
        ----------
        chat : Chat
            Chat to update its metadata
        offset_id : int
            New offset id
        offset_date : int
            New offset date (it's a timestamp)

        Returns
        -------
        Whether the update was successful or not
        """
        return self._graph_db.update_audio_indexer_metadata(
            chat,
            offset_id,
            offset_date,
        )

    def update_audio_indexer_score(
        self,
        chat: graph_models.vertices.Chat,
        score: float,
    ) -> bool:
        """
        Updates audio indexer score of a chat

        Parameters
        ----------
        chat : graph_models.vertices.Chat
            Chat to update its score
        score : float
            New score

        Returns
        -------
        Whether the update was successful or not
        """
        return self._graph_db.update_audio_indexer_score(chat, score)

    def update_username_extractor_score(
        self,
        chat: graph_models.vertices.Chat,
        score: float,
    ) -> bool:
        """
        Updates username extractor score of a chat

        Parameters
        ----------
        chat : graph_models.vertices.Chat
            Chat to update its score
        score : float
            New score

        Returns
        -------
        Whether the update was successful or not
        """
        return self._graph_db.update_username_extractor_score(chat, score)
