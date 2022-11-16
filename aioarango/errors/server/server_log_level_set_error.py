from aioarango.errors.base import ArangoServerError


class ServerLogLevelSetError(ArangoServerError):
    """Failed to set server log levels."""
