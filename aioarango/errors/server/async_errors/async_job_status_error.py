from aioarango.errors.server import ArangoServerError


class AsyncJobStatusError(ArangoServerError):
    """Failed to retrieve async job status."""
