from aioarango.errors.base import ArangoServerError


class ServerRoleError(ArangoServerError):
    """Failed to retrieve server role in a cluster."""
