from aioarango.errors.server import ArangoServerError


class ClusterServerRoleError(ArangoServerError):
    """Failed to retrieve server role."""
