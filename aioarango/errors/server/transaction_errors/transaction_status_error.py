from aioarango.errors.server import ArangoServerError


class TransactionStatusError(ArangoServerError):
    """Failed to retrieve transaction status."""
