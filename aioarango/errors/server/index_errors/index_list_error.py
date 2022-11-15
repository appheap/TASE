from aioarango.errors.base import ArangoServerError


class IndexListError(ArangoServerError):
    """Failed to retrieve collection indexes."""
