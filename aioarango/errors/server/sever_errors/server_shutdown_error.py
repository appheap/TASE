from aioarango.errors.server import ArangoServerError


class ServerShutdownError(ArangoServerError):
    """Failed to initiate shutdown sequence."""
