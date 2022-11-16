from aioarango.errors.base import ArangoServerError


class ServerLogLevelError(ArangoServerError):
    """Failed to retrieve server log levels."""
