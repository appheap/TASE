from aioarango.errors.base import ArangoServerError


class ServerReloadRoutingError(ArangoServerError):
    """Failed to reload routing details."""
