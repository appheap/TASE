from aioarango.errors.server import ArangoServerError


class CollectionUnloadError(ArangoServerError):
    """Failed to unload collection."""
