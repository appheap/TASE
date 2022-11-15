from aioarango.errors.server import ArangoServerError


class ServerTimeError(ArangoServerError):
    """Failed to retrieve server system time."""
