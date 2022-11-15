from aioarango.errors.base import ArangoServerError


class TransactionAbortError(ArangoServerError):
    """Failed to abort transaction."""
