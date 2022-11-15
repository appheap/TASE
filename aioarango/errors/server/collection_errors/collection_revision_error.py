from aioarango.errors.server import ArangoServerError


class CollectionRevisionError(ArangoServerError):
    """Failed to retrieve collection revision."""
