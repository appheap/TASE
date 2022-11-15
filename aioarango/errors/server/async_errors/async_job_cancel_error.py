from aioarango.errors.base import ArangoServerError


class AsyncJobCancelError(ArangoServerError):
    """Failed to cancel async job."""
