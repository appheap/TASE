from aioarango.errors.base import ArangoServerError


class WALTickRangesError(ArangoServerError):
    """Failed to return WAL tick ranges."""
