from __future__ import annotations

from typing import Optional, List, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import ArangoIndexType


class PersistentIndex(BaseArangoIndex):
    type = ArangoIndexType.PERSISTENT

    unique: Optional[bool]
    sparse: Optional[bool]
    estimates: Optional[bool]
    in_background: bool = True
    deduplicate: Optional[bool]
    stored_values: Optional[List[str]]
    cache_enabled: bool = False

    def to_db(
        self,
    ) -> Dict[str, Any,]:
        data = super(PersistentIndex, self).to_db()

        if self.unique is not None:
            data["unique"] = self.unique

        if self.sparse is not None:
            data["sparse"] = self.sparse

        if self.estimates is not None:
            data["estimates"] = self.estimates

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        if self.deduplicate is not None:
            data["deduplicate"] = self.deduplicate

        if self.stored_values is not None:
            data["storedValues"] = self.stored_values

        if self.cache_enabled is not None:
            data["cacheEnabled"] = self.cache_enabled

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[PersistentIndex]:
        index = PersistentIndex(**obj)

        index.in_background = obj.get("inBackground", None)
        index.stored_values = obj.get("storedValues", None)
        index.cache_enabled = obj.get("cacheEnabled", None)

        return index
