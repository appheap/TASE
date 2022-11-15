from aioarango.errors.server import ArangoServerError


class ClusterServerCountError(ArangoServerError):
    """Failed to retrieve cluster server count."""
