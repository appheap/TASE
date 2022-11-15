from aioarango.errors.base import ArangoServerError


class ClusterServerVersionError(ArangoServerError):
    """Failed to retrieve server node version."""
