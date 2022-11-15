from aioarango.errors.base import ArangoServerError


class CollectionListError(ArangoServerError):
    """Failed to retrieve collections."""
