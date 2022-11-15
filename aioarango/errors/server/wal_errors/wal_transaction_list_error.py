from aioarango.errors.server import ArangoServerError


class WALTransactionListError(ArangoServerError):
    """Failed to retrieve running WAL transactions."""
