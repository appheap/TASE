from aioarango.errors.base import ArangoServerError


class AQLQueryExplainError(ArangoServerError):
    """Failed to parse and explain query."""
