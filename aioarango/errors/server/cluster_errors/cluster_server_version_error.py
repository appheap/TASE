from aioarango.errors.server import ArangoServerError


class ClusterServerVersionError(ArangoServerError):
    """Failed to retrieve server node version."""
