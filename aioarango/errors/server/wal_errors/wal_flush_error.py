from aioarango.errors.server import ArangoServerError


class WALFlushError(ArangoServerError):
    """Failed to flush WAL."""
