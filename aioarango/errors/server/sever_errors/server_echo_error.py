from aioarango.errors.base import ArangoServerError


class ServerEchoError(ArangoServerError):
    """Failed to retrieve details on last request."""
