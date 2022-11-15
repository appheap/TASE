from aioarango.errors.base import ArangoServerError


class WALFlushError(ArangoServerError):
    """Failed to flush WAL."""
