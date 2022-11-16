from aioarango.errors.base import ArangoServerError


class AsyncJobClearError(ArangoServerError):
    """Failed to clear async job results."""
