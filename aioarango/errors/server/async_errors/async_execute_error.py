from aioarango.errors.server import ArangoServerError


class AsyncExecuteError(ArangoServerError):
    """Failed to execute async API request."""
