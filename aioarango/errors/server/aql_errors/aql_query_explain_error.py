from aioarango.errors.server import ArangoServerError


class AQLQueryExplainError(ArangoServerError):
    """Failed to parse and explain query."""
