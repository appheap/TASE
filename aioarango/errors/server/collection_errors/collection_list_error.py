from aioarango.errors.server import ArangoServerError


class CollectionListError(ArangoServerError):
    """Failed to retrieve collections."""
