from aioarango.errors.base import ArangoServerError


class CollectionTruncateError(ArangoServerError):
    """Failed to truncate collection."""
