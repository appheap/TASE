from aioarango.errors.server import ArangoServerError


class AsyncJobClearError(ArangoServerError):
    """Failed to clear async job results."""
