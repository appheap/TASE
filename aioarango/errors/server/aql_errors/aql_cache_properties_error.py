from aioarango.errors.server import ArangoServerError


class AQLCachePropertiesError(ArangoServerError):
    """Failed to retrieve query cache properties."""
