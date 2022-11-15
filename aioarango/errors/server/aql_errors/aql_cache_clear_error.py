from aioarango.errors.server import ArangoServerError


class AQLCacheClearError(ArangoServerError):
    """Failed to clear the query cache."""
