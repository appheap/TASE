from aioarango.errors.base import ArangoServerError


class DatabaseListError(ArangoServerError):
    """Failed to retrieve databases."""
