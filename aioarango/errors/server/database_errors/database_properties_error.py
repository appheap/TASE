from aioarango.errors.base import ArangoServerError


class DatabasePropertiesError(ArangoServerError):
    """Failed to retrieve database properties."""
