from aioarango.errors.server import ArangoServerError


class ServerEchoError(ArangoServerError):
    """Failed to retrieve details on last request."""
