from aioarango.errors.base import ArangoServerError


class ClusterServerRoleError(ArangoServerError):
    """Failed to retrieve server role."""
