from aioarango.errors.base import ArangoServerError


class WALConfigureError(ArangoServerError):
    """Failed to configure WAL properties."""
