from aioarango.errors.server import ArangoServerError


class IndexDeleteError(ArangoServerError):
    """Failed to delete collection index."""
