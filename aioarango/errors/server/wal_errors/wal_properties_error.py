from aioarango.errors.base import ArangoServerError


class WALPropertiesError(ArangoServerError):
    """Failed to retrieve WAL properties."""
