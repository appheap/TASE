from aioarango.errors.server import ArangoServerError


class TransactionCommitError(ArangoServerError):
    """Failed to commit transaction."""
