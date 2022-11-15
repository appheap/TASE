from aioarango.errors.server import ArangoServerError


class AQLQueryExecuteError(ArangoServerError):
    """Failed to execute query."""
