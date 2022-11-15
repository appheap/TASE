from aioarango.errors.server import ArangoServerError


class BatchExecuteError(ArangoServerError):
    """Failed to execute batch API request."""
