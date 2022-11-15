from aioarango.errors.server import ArangoServerError


class WALLastTickError(ArangoServerError):
    """Failed to return WAL tick ranges."""
