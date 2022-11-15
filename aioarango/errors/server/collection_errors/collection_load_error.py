from aioarango.errors.server import ArangoServerError


class CollectionLoadError(ArangoServerError):
    """Failed to load collection."""
