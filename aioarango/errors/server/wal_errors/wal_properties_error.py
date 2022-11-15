from aioarango.errors.server import ArangoServerError


class WALPropertiesError(ArangoServerError):
    """Failed to retrieve WAL properties."""
