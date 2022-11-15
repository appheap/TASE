from aioarango.errors.base import ArangoServerError


class CollectionUnloadError(ArangoServerError):
    """Failed to unload collection."""
