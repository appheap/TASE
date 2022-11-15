from aioarango.errors.base import ArangoServerError


class AsyncExecuteError(ArangoServerError):
    """Failed to execute async API request."""
