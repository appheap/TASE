from aioarango.errors.server import ArangoServerError


class DatabasePropertiesError(ArangoServerError):
    """Failed to retrieve database properties."""
