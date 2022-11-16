from aioarango.errors.base import ArangoServerError


class ServerTimeError(ArangoServerError):
    """Failed to retrieve server system time."""
