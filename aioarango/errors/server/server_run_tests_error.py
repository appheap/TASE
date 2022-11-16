from aioarango.errors.base import ArangoServerError


class ServerRunTestsError(ArangoServerError):
    """Failed to execute server tests."""
