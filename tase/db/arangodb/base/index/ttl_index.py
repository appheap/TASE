from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import ArangoIndexType


class TTLIndex(BaseArangoIndex):
    type = ArangoIndexType.TTL

    expiry_time: int
    in_background: Optional[bool]

    def to_db(self) -> Dict[str, Any]:
        data = super(TTLIndex, self).to_db()

        if self.expiry_time is None:
            raise ValueError("Invalid value for `expiry_time`")

        data["expireAfter"] = self.expiry_time

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[TTLIndex]:
        index = TTLIndex(**obj)
        index.expiry_time = obj["expireAfter"]
        index.in_background = obj.get("inBackground", None)
        return index
