from typing import Optional, MutableMapping, List

from pydantic import BaseModel


class AQLQueryCacheEntry(BaseModel):
    """
    Represents an AQL Query cache entry.

    Attributes
    ----------
    hash: str
        Query result's hash
    query: str
        Query string.
    bind_vars: MutableMapping, optional
        Query's bind parameters. this attribute is only shown if tracking for
        bind variables was enabled at server start.
    size : int, optional
        Size of the query result and bind parameters, in bytes
    results : int, optional
        number of documents/rows in the query result
    started: str, optional
        Date and time when the query was stored in the cache
    hits : int, optional
        number of times the result was served from the cache (can be
        `0` for queries that were only stored in the cache but were never accessed
        again afterwards)
    runtime: float, optional
        Query's total run time (in seconds).
    data_sources : list of str, optional
        An array of collections/Views the query was using.
    """

    hash: Optional[str]
    query: Optional[str]
    bind_vars: Optional[MutableMapping[str, str]]
    size: Optional[int]
    results: Optional[int]
    started: Optional[str]
    hits: Optional[int]
    runtime: Optional[float]
    data_sources: Optional[List[str]]
