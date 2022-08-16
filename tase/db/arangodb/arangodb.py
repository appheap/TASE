from arango import ArangoClient
from arango.aql import AQL
from arango.database import StandardDatabase
from arango.graph import Graph
from pydantic import BaseModel
from pydantic.typing import Optional

from tase.configs import ArangoDBConfig
from tase.db.arangodb import ArangoMethods
from tase.db.arangodb.graph.vertices import vertex_classes


class ArangoDB(BaseModel, ArangoMethods):
    arango_client: Optional[ArangoClient]
    db: Optional[StandardDatabase]
    graph: Optional[Graph]
    aql: Optional[AQL]

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self,
        arangodb_config: ArangoDBConfig,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=arangodb_config.db_host_url)
        sys_db = self.arango_client.db(
            "_system",
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        if not sys_db.has_database(arangodb_config.db_name):
            sys_db.create_database(
                arangodb_config.db_name,
            )

        self.db = self.arango_client.db(
            arangodb_config.db_name,
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        self.aql = self.db.aql

        if not self.db.has_graph(arangodb_config.graph_name):
            self.graph = self.db.create_graph(arangodb_config.graph_name)
        else:
            self.graph = self.db.graph(arangodb_config.graph_name)

        for v_class in vertex_classes:
            if not self.graph.has_vertex_collection(v_class._collection_name):
                _collection = self.graph.create_vertex_collection(v_class._collection_name)
            else:
                _collection = self.graph.vertex_collection(v_class._collection_name)
            v_class._collection = _collection
