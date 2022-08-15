from arango.collection import StandardCollection
from pydantic.typing import Optional

from .base_collection_document import BaseCollectionDocument


class BaseDocument(BaseCollectionDocument):
    _collection_name = "base_document"
    _collection: Optional[StandardCollection]
