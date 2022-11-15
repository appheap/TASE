from aioarango.errors.server import ArangoServerError


class ReplicationLoggerFirstTickError(ArangoServerError):
    """Failed to retrieve logger first tick."""
