from arango.collection import StandardCollection
from pydantic.typing import Optional

from tase.db.arangodb.base import BaseCollectionDocument


class BaseDocument(BaseCollectionDocument):
    _collection_name = "base_document"
    _collection: Optional[StandardCollection]
