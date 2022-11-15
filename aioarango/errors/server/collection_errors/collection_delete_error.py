from aioarango.errors.server import ArangoServerError


class CollectionDeleteError(ArangoServerError):
    """Failed to delete collection."""
