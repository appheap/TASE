from aioarango.errors.server import ArangoServerError


class ServerVersionError(ArangoServerError):
    """Failed to retrieve server version."""
