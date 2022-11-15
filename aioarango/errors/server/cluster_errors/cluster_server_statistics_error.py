from aioarango.errors.base import ArangoServerError


class ClusterServerStatisticsError(ArangoServerError):
    """Failed to retrieve DBServer statistics."""
