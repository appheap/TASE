from aioarango.errors.base import ArangoServerError


class BatchExecuteError(ArangoServerError):
    """Failed to execute batch API request."""
