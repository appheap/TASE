from aioarango.errors.base import ArangoServerError


class AQLQueryExecuteError(ArangoServerError):
    """Failed to execute query."""
