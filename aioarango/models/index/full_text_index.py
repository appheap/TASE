from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class FullTextIndex(BaseArangoIndex):
    type = IndexType.FULL_TEXT

    min_length: Optional[int]
    in_background: Optional[bool]

    def to_db(
        self,
    ) -> Dict[str, Any,]:
        data = super(FullTextIndex, self).to_db()

        if self.min_length is not None:
            data["minLength"] = self.min_length

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[FullTextIndex]:
        index = FullTextIndex(**obj)
        return index
