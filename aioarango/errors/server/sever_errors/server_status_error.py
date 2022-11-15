from aioarango.errors.base import ArangoServerError


class ServerStatusError(ArangoServerError):
    """Failed to retrieve server status."""
