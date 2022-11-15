from aioarango.errors.server import ArangoServerError


class ClusterServerStatisticsError(ArangoServerError):
    """Failed to retrieve DBServer statistics."""
