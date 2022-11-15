from aioarango.errors.server import ArangoServerError


class ServerLogLevelError(ArangoServerError):
    """Failed to retrieve server log levels."""
