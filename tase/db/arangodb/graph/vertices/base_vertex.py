from typing import Optional

from arango.collection import VertexCollection

from tase.db.arangodb.base import BaseCollectionDocument


class BaseVertex(BaseCollectionDocument):
    __collection_name__ = "base_vertices"
    __collection__: Optional[VertexCollection]
