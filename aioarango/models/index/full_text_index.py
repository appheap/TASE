from __future__ import annotations

from typing import Optional, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class FullTextIndex(BaseArangoIndex):
    """
    Full-Text Index

    Attributes
    ----------
    type : IndexType
        Type of the index.  must be equal to "fulltext".
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the
        collection, e.g. idx_832910498 .
    fields : list of str
         an array of attribute names. Currently, the array is limited to exactly one attribute.
    min_length : int, optional
        Minimum character length of words to index. Will default
        to a server-defined value if unspecified. It is thus recommended to set
        this value explicitly when creating the index.
    in_background : bool, optional
        The optional attribute inBackground can be set to `true` to create the index
        in the background, which will not write-lock the underlying collection for
        as long as if the index is built in the foreground. The default value is `false`.
    """

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
