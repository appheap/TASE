from aioarango.errors.base import ArangoServerError


class TransactionStatusError(ArangoServerError):
    """Failed to retrieve transaction status."""
