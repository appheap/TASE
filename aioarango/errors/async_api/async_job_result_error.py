from aioarango.errors.base import ArangoServerError


class AsyncJobResultError(ArangoServerError):
    """Failed to retrieve async job result."""
