from typing import Optional

from arango.collection import VertexCollection

from tase.db.arangodb.base import BaseCollectionDocument


class BaseVertex(BaseCollectionDocument):
    _collection_name = "base_vertices"
    _collection: Optional[VertexCollection]
