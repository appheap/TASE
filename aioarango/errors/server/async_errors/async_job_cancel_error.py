from aioarango.errors.server import ArangoServerError


class AsyncJobCancelError(ArangoServerError):
    """Failed to cancel async job."""
