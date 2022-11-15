from aioarango.errors.base import ArangoServerError


class ClusterServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""
