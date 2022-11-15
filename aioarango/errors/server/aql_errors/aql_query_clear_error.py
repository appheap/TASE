from aioarango.errors.server import ArangoServerError


class AQLQueryClearError(ArangoServerError):
    """Failed to clear slow AQL queries."""
