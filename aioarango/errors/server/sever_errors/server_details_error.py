from aioarango.errors.base import ArangoServerError


class ServerDetailsError(ArangoServerError):
    """Failed to retrieve server details."""
