from aioarango.errors.base import ArangoServerError


class IndexDeleteError(ArangoServerError):
    """Failed to delete collection index."""
