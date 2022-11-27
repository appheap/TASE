from __future__ import annotations

from typing import Optional, List, Dict, Any

from .base_arango_index import BaseArangoIndex
from ...enums import IndexType


class PersistentIndex(BaseArangoIndex):
    """
    Attributes
    ----------
    type : IndexType
        Type of the index. Must be equal to "persistent".
    name : str
        An easy-to-remember name for the index to look it up or refer to it in index hints.
        Index names are subject to the same character restrictions as collection names.
        If omitted, a name is auto-generated so that it is unique with respect to the
        collection, e.g. `idx_832910498`.
    fields : list of str
        An array of attribute paths.
    stored_values : list of str, optional
         The optional `storedValues` attribute can contain an array of paths to additional
        attributes to store in the index. These additional attributes cannot be used for
        index lookups or for sorting, but they can be used for projections. This allows an
        index to fully cover more queries and avoid extra document lookups.
        The maximum number of attributes in `storedValues` is `32`.

        It is not possible to create multiple indexes with the same `fields` attributes
        and uniqueness but different `storedValues` attributes. That means the value of
        `storedValues` is not considered by index creation calls when checking if an
        index is already present or needs to be created.

        In unique indexes, only the attributes in fields are checked for uniqueness,
        but the attributes in storedValues are not `checked` for their uniqueness.
        Non-existing attributes are stored as `null` values inside `storedValues`.
    unique : bool, optional
        If `true`, then create a unique index. Defaults to `false`.
        In unique indexes, only the attributes in `fields` are checked for uniqueness,
        but the attributes in `storedValues` are not checked for their uniqueness.
    sparse : bool, optional
        If `true`, then create a sparse index. Defaults to `false`.
    deduplicate : bool, optional
        The attribute controls whether inserting duplicate index values
        from the same document into a unique array index will lead to a unique constraint
        error or not. The default value is `true`, so only a single instance of each
        non-unique index value will be inserted into the index per document. Trying to
        insert a value into the index that already exists in the index will always fail,
        regardless of the value of this attribute.
    estimates : bool, optional
        This attribute controls whether index selectivity estimates are maintained for the
        index. Not maintaining index selectivity estimates can have a slightly positive
        impact on write performance.

        The downside of turning off index selectivity estimates will be that
        the query optimizer will not be able to determine the usefulness of different
        competing indexes in AQL queries when there are multiple candidate indexes to
        choose from.

        The `estimates` attribute is optional and defaults to `true` if not set. It will
        have no effect on indexes other than `persistent`.
    cache_enabled : bool, default : False
        This attribute controls whether an extra in-memory hash cache is
        created for the index. The hash cache can be used to speed up index lookups.
        The cache can only be used for queries that look up all index attributes via
        an equality lookup (`==`). The hash cache cannot be used for range scans,
        partial lookups or sorting.

        The cache will be populated lazily upon reading data from the index. Writing data
        into the collection or updating existing data will invalidate entries in the
        cache. The cache may have a negative effect on performance in case index values
        are updated more often than they are read.

        The maximum size of cache entries that can be stored is currently 4 MB, i.e.
        the cumulated size of all index entries for any index lookup value must be
        less than 4 MB. This limitation is there to avoid storing the index entries
        of "super nodes" in the cache.

        `cacheEnabled` defaults to `false` and should only be used for indexes that
        are known to benefit from an extra layer of caching.
    in_background : bool, default : True
        This attribute can be set to `true` to create the index
        in the background, which will not write-lock the underlying collection for
        as long as if the index is built in the foreground. The default value is `false`.

    """

    type = IndexType.PERSISTENT

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
        return index
