from aioarango.errors.base import ArangoServerError


class DatabaseDeleteError(ArangoServerError):
    """Failed to delete database."""
