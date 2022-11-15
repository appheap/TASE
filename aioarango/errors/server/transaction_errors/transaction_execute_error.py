from aioarango.errors.server import ArangoServerError


class TransactionExecuteError(ArangoServerError):
    """Failed to execute raw transaction."""
