from aioarango.errors.server import ArangoServerError


class ServerMetricsError(ArangoServerError):
    """Failed to retrieve server metrics."""
