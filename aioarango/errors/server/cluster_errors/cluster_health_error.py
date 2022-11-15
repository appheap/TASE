from aioarango.errors.server import ArangoServerError


class ClusterHealthError(ArangoServerError):
    """Failed to retrieve DBServer health."""
