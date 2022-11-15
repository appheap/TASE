from aioarango.errors.server import ArangoServerError


class WALTailError(ArangoServerError):
    """Failed to return WAL tick ranges."""
