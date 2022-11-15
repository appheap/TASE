from aioarango.errors.server import ArangoServerError


class CollectionCreateError(ArangoServerError):
    """Failed to create collection."""
