from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class MultiDimensionalIndex(BaseArangoIndex):
    """
    Attributes
    ----------
    type : IndexType
        Type of the index. must be equal to "zkd".
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the
        collection, e.g. `idx_832910498`.
    fields : list of str
        An array of attribute names used for each dimension. Array expansions are not allowed.
    in_background : bool, optional
        The optional attribute `inBackground` can be set to `true` to create the index
        in the background, which will not write-lock the underlying collection for
        as long as if the index is built in the foreground. The default value is `false`.
    field_value_types : str, default : "double"
        Must be equal to "double". Currently only doubles are supported as values.
    """

    type = IndexType.MULTI_DIMENSIONAL

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
