from arango.collection import VertexCollection
from pydantic.typing import Optional

from .base_collection_document import BaseCollectionDocument


class BaseVertex(BaseCollectionDocument):
    _collection_name = "base_vertices"
    _collection: Optional[VertexCollection]
