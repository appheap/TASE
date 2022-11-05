from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import ArangoIndexType


class HashIndex(BaseArangoIndex):
    type = ArangoIndexType.HASH

    unique: Optional[bool]
    sparse: Optional[bool]
    deduplicate: Optional[bool]
    in_background: Optional[bool]

    def to_db(
        self,
    ) -> Dict[str, Any,]:
        data = super(HashIndex, self).to_db()

        if self.unique is not None:
            data["unique"] = self.unique

        if self.sparse is not None:
            data["sparse"] = self.sparse

        if self.deduplicate is not None:
            data["deduplicate"] = self.deduplicate

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[HashIndex]:
        index = HashIndex(**obj)

        index.in_background = obj.get("inBackground", None)

        return index
