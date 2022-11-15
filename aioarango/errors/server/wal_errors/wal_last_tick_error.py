from aioarango.errors.base import ArangoServerError


class WALLastTickError(ArangoServerError):
    """Failed to return WAL tick ranges."""
