from aioarango.errors.base import ArangoServerError


class TransactionCommitError(ArangoServerError):
    """Failed to commit transaction."""
