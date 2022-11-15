from aioarango.errors.base import ArangoServerError


class CollectionRevisionError(ArangoServerError):
    """Failed to retrieve collection revision."""
