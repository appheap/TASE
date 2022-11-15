from aioarango.errors.server import ArangoServerError


class AQLCacheEntriesError(ArangoServerError):
    """Failed to retrieve AQL cache entries."""
