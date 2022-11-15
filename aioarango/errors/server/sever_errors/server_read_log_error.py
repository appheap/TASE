from aioarango.errors.server import ArangoServerError


class ServerReadLogError(ArangoServerError):
    """Failed to retrieve global log."""
