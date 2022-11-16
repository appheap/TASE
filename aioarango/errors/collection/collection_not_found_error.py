from aioarango.errors.base import ArangoServerError


class CollectionNotFoundError(ArangoServerError):
    """Collection does not exist."""
