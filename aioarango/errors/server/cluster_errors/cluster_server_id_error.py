from aioarango.errors.server import ArangoServerError


class ClusterServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""
