from aioarango.errors.server import ArangoServerError


class TransactionAbortError(ArangoServerError):
    """Failed to abort transaction."""
