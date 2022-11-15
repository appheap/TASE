from aioarango.errors.server import ArangoServerError


class DatabaseDeleteError(ArangoServerError):
    """Failed to delete database."""
