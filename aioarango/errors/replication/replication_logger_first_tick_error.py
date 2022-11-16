from aioarango.errors.base import ArangoServerError


class ReplicationLoggerFirstTickError(ArangoServerError):
    """Failed to retrieve logger first tick."""
