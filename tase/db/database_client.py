from typing import Optional

import pyrogram

from .arangodb import ArangoDB, graph as graph_models
from .arangodb.document import ArangoDocumentMethods
from .arangodb.enums import AudioType
from .arangodb.graph import ArangoGraphMethods
from .elasticsearchdb import ElasticsearchDatabase
from .elasticsearchdb.models import ElasticSearchMethods
from .helpers import ChatScores
from ..configs import ArangoDBConfig, ElasticConfig
from ..errors import PlaylistDoesNotExists
from ..my_logger import logger


class DatabaseClient:
    es_db: ElasticsearchDatabase
    arangodb: ArangoDB

    index: ElasticSearchMethods = ElasticSearchMethods()
    graph: ArangoGraphMethods = ArangoGraphMethods()
    document: ArangoDocumentMethods = ArangoDocumentMethods()

    def __init__(
        self,
        elasticsearch_config: ElasticConfig,
        arangodb_config: ArangoDBConfig,
    ):
        self.es_db = ElasticsearchDatabase(elasticsearch_config=elasticsearch_config)
        self.arangodb = ArangoDB()

        self._arangodb_config = arangodb_config

    async def init_databases(
        self,
        update_arango_indexes: bool = False,
    ):
        await self.es_db.init_database()
        await self.arangodb.initialize(self._arangodb_config, update_arango_indexes)

    async def get_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> bool:
        """
        Create the audio vertex and document in the arangodb and audio document in the elasticsearch.
        These entities are created if they do not already exist in the database.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to use for creating the audio entities.
        telegram_client_id : int
            ID of the telegram client making this request.
        chat_id : int
            ID of the telegram chat this message belongs to.
        audio_type : AudioType
            Type of the audio to store in the databases.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        bool
            Whether the operation was successful or not.
        """
        if telegram_message is None or telegram_message.audio is None:
            return False

        try:
            audio_vertex = await self.graph.get_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
            audio_doc = await self.document.get_or_create_audio(telegram_message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.get_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False

    async def update_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
        chat_id: int,
        audio_type: AudioType,
        chat_scores: ChatScores,
    ) -> bool:
        """
        Create the audio vertex and document in the arangodb and audio document in the elasticsearch.
        These entities are created if they do not already exist in the database. Otherwise, they will get updated.

        Parameters
        ----------
        telegram_message : pyrogram.types.Message
            Telegram message to use for creating the audio entities.
        telegram_client_id : int
            ID of the telegram client making this request.
        chat_id : int
            ID of the telegram chat this message belongs to.
        audio_type : AudioType
            Type of the audio to store in the databases.
        chat_scores : ChatScores
            Scores of the parent chat.

        Returns
        -------
        bool
            Whether the operation was successful or not.
        """
        if telegram_message is None or telegram_client_id is None:
            return False

        try:
            audio_vertex = await self.graph.update_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
            audio_doc = await self.document.update_or_create_audio(telegram_message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.update_or_create_audio(telegram_message, chat_id, audio_type, chat_scores)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False

    async def invalidate_old_audios(
        self,
        chat_id: int,
        message_id: int,
        excluded_audio_vertex_key: Optional[str] = None,
    ) -> None:
        if not chat_id or message_id is None:
            return

        await self.graph.mark_old_audio_vertices_as_deleted(
            chat_id=chat_id,
            message_id=message_id,
            excluded_key=excluded_audio_vertex_key,
        )

        await self.document.delete_old_audio_caches(
            chat_id=chat_id,
            message_id=message_id,
        )

        await self.index.mark_old_audios_as_deleted(
            chat_id=chat_id,
            message_id=message_id,
            excluded_id=excluded_audio_vertex_key,
        )

    async def mark_chat_audios_as_deleted(
        self,
        chat_id: int,
    ) -> None:
        """
        Mark `Audio` vertices in ArangoDB and documents in the Elasticsearch with the given `chat_id` as deleted.

        Parameters
        ----------
        chat_id : int
            ID of the chat the audio documents belongs to.

        """
        if chat_id is None:
            return

        await self.graph.mark_chat_audios_as_deleted(chat_id=chat_id)
        await self.index.mark_chat_audios_as_deleted(chat_id=chat_id)

    async def remove_playlist(
        self,
        user: graph_models.vertices.User,
        playlist_key: str,
        deleted_at: int,
    ) -> bool:
        """
        Remove the `Playlist` with the given `playlist_key` and return whether the deletion was successful or not.

        This method deleted the playlist from both `ArangoDB` and `ElasticSearch`.

        Parameters
        ----------
        user : graph_models.vertices.User
            User that playlist belongs to
        playlist_key : str
            Key of the playlist to delete
        deleted_at : int
            Timestamp of the deletion

        Raises
        ------
        PlaylistDoesNotExists
            If the user does not have a playlist with the given `playlist_key` parameter

        Returns
        -------
        bool
            Whether the deletion operation was successful or not.
        """
        if not user or not playlist_key or deleted_at is None:
            return False

        graph_updated = await self.graph.remove_playlist(user, playlist_key, deleted_at)

        try:
            es_updated = await self.index.remove_playlist(user, playlist_key, deleted_at)
        except PlaylistDoesNotExists:
            es_updated = True

        return graph_updated & es_updated
