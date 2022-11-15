from aioarango.errors.base import ArangoServerError


class AQLQueryClearError(ArangoServerError):
    """Failed to clear slow AQL queries."""
