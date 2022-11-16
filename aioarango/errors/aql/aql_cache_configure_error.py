from aioarango.errors.base import ArangoServerError


class AQLCacheConfigureError(ArangoServerError):
    """Failed to configure query cache properties."""
