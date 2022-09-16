from typing import Optional

from arango.collection import StandardCollection

from tase.db.arangodb.base import BaseCollectionDocument


class BaseDocument(BaseCollectionDocument):
    _collection_name = "base_document"
    _collection: Optional[StandardCollection]
