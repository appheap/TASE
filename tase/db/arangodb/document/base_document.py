from typing import Optional

from arango.collection import StandardCollection

from tase.db.arangodb.base import BaseCollectionDocument


class BaseDocument(BaseCollectionDocument):
    __collection_name__ = "base_document"
    __collection__: Optional[StandardCollection]
