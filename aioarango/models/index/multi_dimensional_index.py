from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class MultiDimensionalIndex(BaseArangoIndex):
    type = IndexType.TTL

    unique: Optional[bool]
    in_background: Optional[bool]
    field_value_types: str = "double"

    def to_db(self) -> Dict[str, Any]:
        data = super(MultiDimensionalIndex, self).to_db()

        if self.field_value_types is None or not len(self.field_value_types):
            raise ValueError("Invalid value for `field_value_types`")

        data["fieldValueTypes"] = self.field_value_types

        if self.unique is not None:
            data["unique"] = self.unique

        if self.in_background is not None:
            data["inBackground"] = self.in_background

        return data

    @classmethod
    def from_db(
        cls,
        obj: Dict[str, Any],
    ) -> Optional[MultiDimensionalIndex]:
        index = MultiDimensionalIndex(**obj)
        return index
