from aioarango.errors.server import ArangoServerError


class AQLCacheConfigureError(ArangoServerError):
    """Failed to configure query cache properties."""
