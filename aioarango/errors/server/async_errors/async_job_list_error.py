from aioarango.errors.server import ArangoServerError


class AsyncJobListError(ArangoServerError):
    """Failed to retrieve async jobs."""
