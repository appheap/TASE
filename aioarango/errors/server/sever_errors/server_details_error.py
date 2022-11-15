from aioarango.errors.server import ArangoServerError


class ServerDetailsError(ArangoServerError):
    """Failed to retrieve server details."""
