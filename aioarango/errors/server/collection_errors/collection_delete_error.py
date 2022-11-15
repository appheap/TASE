from aioarango.errors.base import ArangoServerError


class CollectionDeleteError(ArangoServerError):
    """Failed to delete collection."""
