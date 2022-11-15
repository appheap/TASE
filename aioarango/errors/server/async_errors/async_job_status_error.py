from aioarango.errors.base import ArangoServerError


class AsyncJobStatusError(ArangoServerError):
    """Failed to retrieve async job status."""
