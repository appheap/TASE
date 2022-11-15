from aioarango.errors.server import ArangoServerError


class WALTickRangesError(ArangoServerError):
    """Failed to return WAL tick ranges."""
