from aioarango.errors.server import ArangoServerError


class TransactionInitError(ArangoServerError):
    """Failed to initialize transaction."""
