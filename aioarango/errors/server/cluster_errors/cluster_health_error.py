from aioarango.errors.base import ArangoServerError


class ClusterHealthError(ArangoServerError):
    """Failed to retrieve DBServer health."""
