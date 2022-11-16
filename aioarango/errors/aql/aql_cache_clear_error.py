from aioarango.errors.base import ArangoServerError


class AQLCacheClearError(ArangoServerError):
    """Failed to clear the query cache."""
