from aioarango.errors.base import ArangoServerError


class ServerStatisticsError(ArangoServerError):
    """Failed to retrieve server statistics."""
