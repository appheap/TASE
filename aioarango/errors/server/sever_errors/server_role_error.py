from aioarango.errors.server import ArangoServerError


class ServerRoleError(ArangoServerError):
    """Failed to retrieve server role in a cluster."""
