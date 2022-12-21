from typing import Optional

from pydantic import BaseModel

from aioarango import ArangoClient
from aioarango.api import StandardDatabase, Graph, AQL
from aioarango.models import GraphInfo, EdgeDefinition
from tase.configs import ArangoDBConfig
from tase.db.arangodb.graph.vertices import vertex_classes
from .document import document_classes
from .graph.edges import edge_classes


class ArangoDB(
    BaseModel,
):
    arango_client: Optional[ArangoClient]
    db: Optional[StandardDatabase]
    graph: Optional[Graph]
    aql: Optional[AQL]

    class Config:
        arbitrary_types_allowed = True

    async def initialize(
        self,
        arangodb_config: ArangoDBConfig,
        update_indexes: bool = False,
    ):
        # Initialize the client for ArangoDB.
        self.arango_client = ArangoClient(hosts=arangodb_config.db_host_url)
        sys_db = await self.arango_client.db(
            "_system",
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        if not await sys_db.has_database(arangodb_config.db_name):
            await sys_db.create_database(
                arangodb_config.db_name,
            )

        self.db = await self.arango_client.db(
            arangodb_config.db_name,
            username=arangodb_config.db_username,
            password=arangodb_config.db_password,
        )

        self.aql = self.db.aql

        if not await self.db.has_graph(arangodb_config.graph_name):
            self.graph = await self.db.create_graph(GraphInfo(name=arangodb_config.graph_name))
        else:
            self.graph = self.db.graph(arangodb_config.graph_name)

        for v_class in vertex_classes:
            if not await self.graph.has_vertex_collection(v_class.__collection_name__):
                _collection = await self.graph.create_vertex_collection(v_class.__collection_name__)
            else:
                _collection = self.graph.vertex_collection(v_class.__collection_name__)
            v_class.__graph_name__ = arangodb_config.graph_name
            v_class.__collection__ = _collection
            v_class.__aql__ = self.aql
            if update_indexes:
                await v_class.update_indexes()

        for e_class in edge_classes:
            if not await self.graph.has_edge_definition(e_class.__collection_name__):
                _collection = await self.graph.create_edge_definition(
                    EdgeDefinition(
                        collection=e_class.__collection_name__,
                        from_=e_class.from_vertex_collections(),
                        to=e_class.from_vertex_collections(),
                    )
                )
            else:
                _collection = self.graph.edge_collection(e_class.__collection_name__)
            e_class.__graph_name__ = arangodb_config.graph_name
            e_class.__collection__ = _collection
            e_class.__aql__ = self.aql

            if update_indexes:
                await e_class.update_indexes()

        for doc in document_classes:
            if not await self.db.has_collection(doc.__collection_name__):
                _collection = await self.db.create_collection(doc.__collection_name__)
            else:
                _collection = self.db.collection(doc.__collection_name__)
            doc.__graph_name__ = arangodb_config.graph_name
            doc.__collection__ = _collection
            doc.__aql__ = self.aql

            if update_indexes:
                await doc.update_indexes()
