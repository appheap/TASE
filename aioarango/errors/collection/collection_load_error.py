from aioarango.errors.base import ArangoServerError


class CollectionLoadError(ArangoServerError):
    """Failed to load collection."""
