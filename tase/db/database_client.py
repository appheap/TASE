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
        self.arangodb = ArangoDB(arangodb_config=arangodb_config)

    def get_or_create_audio(
        self,
        message: pyrogram.types.Message,
        telegram_client_id: int,
    ):
        if message is None or message.audio is None:
            return
        try:
            self.graph.get_or_create_audio(message)
            self.document.get_or_create_audio(message, telegram_client_id)
            self.index.get_or_create_audio(message)
        except Exception as e:
            logger.exception(e)

    def update_or_create_audio(
        self,
        telegram_message: pyrogram.types.Message,
        telegram_client_id: int,
    ):
        try:
            self.graph.update_or_create_audio(telegram_message)
            self.document.update_or_create_audio(telegram_message, telegram_client_id)
            self.index.update_or_create_audio(telegram_message)
        except Exception as e:
            logger.exception(e)
