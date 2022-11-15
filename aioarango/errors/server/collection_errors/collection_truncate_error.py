from aioarango.errors.server import ArangoServerError


class CollectionTruncateError(ArangoServerError):
    """Failed to truncate collection."""
