import asyncio

import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.db.elasticsearchdb import models
from .arangodb import ArangoDB
from .arangodb.document import ArangoDocumentMethods
from .arangodb.enums import AudioType
from .arangodb.graph import ArangoGraphMethods
from .elasticsearchdb import ElasticsearchDatabase
from .elasticsearchdb.models import ElasticSearchMethods
from ..configs import ArangoDBConfig, ElasticConfig
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
        message: pyrogram.types.Message,
        telegram_client_id: int,
        chat_id: int,
        audio_type: AudioType,
    ) -> bool:
        """
        Create the audio vertex and document in the arangodb and audio document in the elasticsearch.
        These entities are created if they do not already exist in the database.

        Parameters
        ----------
        message : pyrogram.types.Message
            Telegram message to use for creating the audio entities.
        telegram_client_id : int
            ID of the telegram client making this request.
        chat_id : int
            ID of the telegram chat this message belongs to.
        audio_type : AudioType
            Type of the audio to store in the databases.

        Returns
        -------
        bool
            Whether the operation was successful or not.

        Raises
        ------
        TelegramMessageWithNoAudio
            If `telegram_message` argument does not contain any valid audio file.

        """
        if message is None or message.audio is None:
            return False

        try:
            audio_vertex = await self.graph.get_or_create_audio(message, chat_id, audio_type)
            audio_doc = await self.document.get_or_create_audio(message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.get_or_create_audio(message, chat_id, audio_type)
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
        audio_type,
    ) -> bool:
        if telegram_message is None or telegram_client_id is None:
            return False

        try:
            audio_vertex = await self.graph.update_or_create_audio(telegram_message, chat_id, audio_type)
            audio_doc = await self.document.update_or_create_audio(telegram_message, telegram_client_id, chat_id)
            es_audio_doc = await self.index.update_or_create_audio(telegram_message, chat_id, audio_type)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False

    async def mark_audio_as_invalid(
        self,
        audio_key: str,
    ) -> None:
        if not audio_key:
            return
        # todo: what about users who have already downloaded this file before invalidation had happened?

        audio_vertex, audio_doc = await asyncio.gather(*(self.graph.get_audio_by_key(audio_key), self.index.get_audio_by_id(audio_key)))
        if audio_vertex and isinstance(audio_vertex, graph_models.vertices.Audio):
            await audio_vertex.mark_as_non_audio()

        if audio_doc and isinstance(audio_doc, models.Audio):
            await audio_doc.mark_as_non_audio()

    async def mark_audio_as_deleted(
        self,
        audio_key: str,
    ) -> None:
        if not audio_key:
            return

        # todo: what about users who have already downloaded this file before deletion had happened?

        audio_vertex, audio_doc = await asyncio.gather(*(self.graph.get_audio_by_key(audio_key), self.index.get_audio_by_id(audio_key)))
        if audio_vertex and isinstance(audio_vertex, graph_models.vertices.Audio):
            await audio_vertex.mark_as_deleted()

        if audio_doc and isinstance(audio_doc, models.Audio):
            await audio_doc.mark_as_deleted()
