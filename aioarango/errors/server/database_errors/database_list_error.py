from aioarango.errors.server import ArangoServerError


class DatabaseListError(ArangoServerError):
    """Failed to retrieve databases."""
