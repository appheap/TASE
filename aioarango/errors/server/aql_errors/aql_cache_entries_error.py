from aioarango.errors.base import ArangoServerError


class AQLCacheEntriesError(ArangoServerError):
    """Failed to retrieve AQL cache entries."""
