from aioarango.errors.base import ArangoServerError


class AQLCachePropertiesError(ArangoServerError):
    """Failed to retrieve query cache properties."""
