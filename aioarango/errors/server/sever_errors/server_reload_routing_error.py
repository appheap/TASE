from aioarango.errors.server import ArangoServerError


class ServerReloadRoutingError(ArangoServerError):
    """Failed to reload routing details."""
