from aioarango.errors.base import ArangoServerError


class ServerReadLogError(ArangoServerError):
    """Failed to retrieve global log."""
