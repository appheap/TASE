from aioarango.errors.server import ArangoServerError


class ServerLogLevelSetError(ArangoServerError):
    """Failed to set server log levels."""
