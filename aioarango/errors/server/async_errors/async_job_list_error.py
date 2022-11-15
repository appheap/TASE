from aioarango.errors.base import ArangoServerError


class AsyncJobListError(ArangoServerError):
    """Failed to retrieve async jobs."""
