from aioarango.errors.server import ArangoServerError


class WALConfigureError(ArangoServerError):
    """Failed to configure WAL properties."""
