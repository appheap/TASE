from aioarango.errors.server import ArangoServerError


class AsyncJobResultError(ArangoServerError):
    """Failed to retrieve async job result."""
