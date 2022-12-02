from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class TTLIndex(BaseArangoIndex):
    """
    Attributes
    ----------
    type : str
        Type of the index. must be equal to "ttl".
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the
        collection, e.g. `idx_832910498`.
    fields : list of str
        An array with exactly `one` attribute path.
    expiry_time : int
        The time interval (in seconds) from the point in time stored in the `fields`
        attribute after which the documents count as expired. Can be set to `0` to let
        documents expire as soon as the server time passes the point in time stored in
        the document attribute, or to a higher number to delay the expiration.
    in_background : bool
        The optional attribute `inBackground` can be set to `true` to create the index
        in the background, which will not write-lock the underlying collection for
        as long as if the index is built in the foreground. The default value is `false`.

    unique : bool, optional
        Whether the index in unique or not.
    sparse : bool, optional
        Whether the index is sparse or not.
    """

    type = IndexType.TTL

    expiry_time: int
    in_background: Optional[bool]

    # todo:  this attributes must not be set when the object is used to create an index in arangodb.
    sparse: Optional[bool]
    unique: Optional[bool]

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
        return index
