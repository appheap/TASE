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
