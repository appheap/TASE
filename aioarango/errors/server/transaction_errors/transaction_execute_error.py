from aioarango.errors.base import ArangoServerError


class TransactionExecuteError(ArangoServerError):
    """Failed to execute raw transaction."""
