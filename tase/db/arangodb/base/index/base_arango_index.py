from __future__ import annotations

from typing import List, Any, Dict, Optional

from pydantic import BaseModel, Field

from tase.db.arangodb.enums import ArangoIndexType


class BaseArangoIndex(BaseModel):
    id: Optional[str]
    version: int = Field(default=1)
    type: ArangoIndexType
    name: str
    fields: List[str]
    selectivity: Optional[float]

    def to_db(self) -> Dict[str, Any]:
        if self.type is None or self.type == ArangoIndexType.UNKNOWN:
            raise ValueError("Invalid value for `type`")

        if self.name is None or not len(self.name):
            raise ValueError("Invalid value for `name`")

        if self.fields is None or not len(self.fields):
            raise ValueError("Invalid value for `fields`")

        data = {
            "type": self.type.value,
            "name": f"{self.name}__{self.version}",
            "fields": self.fields,
        }

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[BaseArangoIndex]:
        if obj is None or not len(obj):
            return None

        if "type" in obj:
            try:
                index_type = ArangoIndexType(obj["type"])
            except Exception:
                print(obj)
                raise ValueError("Invalid value for `type`")
            else:
                from tase.db.arangodb.base.index import EdgeIndex
                from tase.db.arangodb.base.index import FullTextIndex
                from tase.db.arangodb.base.index import GeoIndex
                from tase.db.arangodb.base.index import HashIndex
                from tase.db.arangodb.base.index import InvertedIndex
                from tase.db.arangodb.base.index import PersistentIndex
                from tase.db.arangodb.base.index import PrimaryIndex
                from tase.db.arangodb.base.index import SkipListIndex
                from tase.db.arangodb.base.index import TTLIndex
                from tase.db.arangodb.base.index import MultiDimensionalIndex

                if index_type == ArangoIndexType.EDGE:
                    index = EdgeIndex.from_db(obj)
                elif index_type == ArangoIndexType.FULL_TEXT:
                    index = FullTextIndex.from_db(obj)
                elif index_type == ArangoIndexType.GEO:
                    index = GeoIndex.from_db(obj)
                elif index_type == ArangoIndexType.HASH:
                    index = HashIndex.from_db(obj)
                elif index_type == ArangoIndexType.INVERTED:
                    index = InvertedIndex.from_db(obj)
                elif index_type == ArangoIndexType.MULTI_DIMENSIONAL:
                    index = MultiDimensionalIndex.from_db(obj)
                elif index_type == ArangoIndexType.PERSISTENT:
                    index = PersistentIndex.from_db(obj)
                elif index_type == ArangoIndexType.PRIMARY:
                    index = PrimaryIndex.from_db(obj)
                elif index_type == ArangoIndexType.SKIPLIST:
                    index = SkipListIndex.from_db(obj)
                elif index_type == ArangoIndexType.TTL:
                    index = TTLIndex.from_db(obj)
                else:
                    raise ValueError("Invalid value for `type`")

                if ":" in index.name:
                    name, version = index.name.split("__")
                    index.name = name
                    index.version = version

                return index

        else:
            raise ValueError("Invalid value for `type`")
