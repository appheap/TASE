from aioarango.errors.server import ArangoServerError


class ServerStatusError(ArangoServerError):
    """Failed to retrieve server status."""
