from aioarango.errors.server import ArangoServerError


class IndexListError(ArangoServerError):
    """Failed to retrieve collection indexes."""
