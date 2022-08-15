from arango.collection import VertexCollection
from pydantic.typing import Optional

from tase.db.arangodb.models.base import BaseCollectionDocument


class BaseVertex(BaseCollectionDocument):
    _collection_name = "base_vertices"
    _collection: Optional[VertexCollection]
