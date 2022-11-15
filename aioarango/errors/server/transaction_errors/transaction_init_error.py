from aioarango.errors.base import ArangoServerError


class TransactionInitError(ArangoServerError):
    """Failed to initialize transaction."""
