from aioarango.errors.base import ArangoServerError


class WALTransactionListError(ArangoServerError):
    """Failed to retrieve running WAL transactions."""
