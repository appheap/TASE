from aioarango.errors.base import ArangoServerError


class ServerShutdownError(ArangoServerError):
    """Failed to initiate shutdown sequence."""
