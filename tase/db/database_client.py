import pyrogram

from .arangodb import ArangoDB
from .arangodb.document import ArangoDocumentMethods
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
    ) -> bool:
        if message is None or message.audio is None:
            return False

        try:
            audio_vertex = await self.graph.get_or_create_audio(message)
            audio_doc = await self.document.get_or_create_audio(message, telegram_client_id)
            es_audio_doc = await self.index.get_or_create_audio(message)
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
    ) -> bool:
        if telegram_message is None or telegram_client_id is None:
            return False

        try:
            audio_vertex = await self.graph.update_or_create_audio(telegram_message)
            audio_doc = await self.document.update_or_create_audio(telegram_message, telegram_client_id)
            es_audio_doc = await self.index.update_or_create_audio(telegram_message)
        except Exception as e:
            logger.exception(e)
        else:
            if audio_vertex is not None and audio_doc is not None and es_audio_doc is not None:
                return True

        return False
