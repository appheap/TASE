from aioarango.errors.base import ArangoServerError


class CollectionCreateError(ArangoServerError):
    """Failed to create collection."""
