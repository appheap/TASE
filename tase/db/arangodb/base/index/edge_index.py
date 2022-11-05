from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import ArangoIndexType


class EdgeIndex(BaseArangoIndex):
    type = ArangoIndexType.EDGE

    unique: Optional[bool]
    sparse: Optional[bool]

    def to_db(
        self,
    ) -> Dict[str, Any,]:
        data = super(EdgeIndex, self).to_db()

        if self.unique is not None:
            data["unique"] = self.unique

        if self.sparse is not None:
            data["sparse"] = self.sparse

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[EdgeIndex]:
        index = EdgeIndex(**obj)
        return index
