from aioarango.errors.base import ArangoServerError


class ServerVersionError(ArangoServerError):
    """Failed to retrieve server version."""
