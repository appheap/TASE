from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CursorStats(BaseModel):
    """
    Statistics of a cursor after running a query.


    Attributes
    ----------
    modified : int, optional
         The total number of data-modification operations successfully executed.
    ignored : int, optional
        The total number of data-modification operations that were unsuccessful,
        but have been ignored because of query option `ignoreErrors`
    scanned_full : int, optional
        The total number of documents iterated over when scanning a collection
        without an index. Documents scanned by sub-queries will be included in the result, but
        operations triggered by built-in or user-defined AQL functions will not.
    scanned_index : int, optional
        The total number of documents iterated over when scanning a collection using
        an index. Documents scanned by sub-queries will be included in the result, but operations
        triggered by built-in or user-defined AQL functions will not.
    cursors_created : int, optional
        The total number of cursor objects created during query execution. Cursor
        objects are created for index lookups.
    cursors_rearmed : int, optional
        The total number of times an existing cursor object was repurposed.
        Repurposing an existing cursor object is normally more efficient compared to destroying an
        existing cursor object and creating a new one from scratch.
    cache_hits : int, optional
        The total number of index entries read from in-memory caches for indexes
        of type edge or persistent. This value will only be non-zero when reading from indexes
        that have an in-memory cache enabled, and when the query allows using the in-memory
        cache (i.e. using equality lookups on all index attributes).
    cache_misses : int, optional
        The total number of cache read attempts for index entries that could not
        be served from in-memory caches for indexes of type edge or persistent. This value will
        only be non-zero when reading from indexes that have an in-memory cache enabled, the
        query allows using the in-memory cache (i.e. using equality lookups on all index attributes)
        and the looked up values are not present in the cache.
    filtered : int, optional
        The total number of documents that were removed after executing a filter condition
        in a `FilterNode` or another node that post-filters data.
        Note that `IndexNodes` can also filter documents by selecting only the required index range
        from a collection, and the filtered value only indicates how much filtering was done by a
        post filter in the `IndexNode` itself or following `FilterNodes`.
        `EnumerateCollectionNodes` and `TraversalNodes` can also apply filter conditions and can
        reported the number of filtered documents.

    execution_time : float, optional
        Time it took to run this query on the sever side (in seconds).
    http_requests : int, optional




    """

    modified: Optional[int]
    ignored: Optional[int]
    scanned_full: Optional[int]
    scanned_index: Optional[int]
    cursors_created: Optional[int]
    cursors_rearmed: Optional[int]
    cache_hits: Optional[int]
    filtered: Optional[int]
    full_count: Optional[int]
    peak_memory_usage: Optional[float]

    execution_time: Optional[float]
    http_requests: Optional[int]
    cache_misses: Optional[int]

    @classmethod
    def parse_from_dict(cls, d: dict) -> Optional[CursorStats]:
        if not d:
            return None

        return CursorStats(
            modified=d.get("writesExecuted", None),
            ignored=d.get("writesIgnored", None),
            scanned_full=d.get("scannedFull", None),
            scanned_index=d.get("scannedIndex", None),
            cursors_created=d.get("cursorsCreated", None),
            cursors_rearmed=d.get("cursorsRearmed", None),
            cache_hits=d.get("cacheHits", None),
            cache_misses=d.get("cacheMisses", None),
            filtered=d.get("filtered", None),
            full_count=d.get("fullCount", None),
            peak_memory_usage=d.get("peakMemoryUsage", None),
            execution_time=d.get("executionTime", None),
            http_requests=d.get("httpRequests", None),
        )
