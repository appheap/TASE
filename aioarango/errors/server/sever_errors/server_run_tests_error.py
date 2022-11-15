from aioarango.errors.server import ArangoServerError


class ServerRunTestsError(ArangoServerError):
    """Failed to execute server tests."""
