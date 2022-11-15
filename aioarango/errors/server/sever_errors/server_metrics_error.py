from aioarango.errors.base import ArangoServerError


class ServerMetricsError(ArangoServerError):
    """Failed to retrieve server metrics."""
