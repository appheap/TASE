from aioarango.errors.server import ArangoServerError


class ServerStatisticsError(ArangoServerError):
    """Failed to retrieve server statistics."""
