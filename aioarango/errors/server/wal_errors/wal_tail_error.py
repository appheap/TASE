from aioarango.errors.base import ArangoServerError


class WALTailError(ArangoServerError):
    """Failed to return WAL tick ranges."""
