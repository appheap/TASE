from aioarango.errors.base import ArangoServerError


class ClusterServerCountError(ArangoServerError):
    """Failed to retrieve cluster server count."""
