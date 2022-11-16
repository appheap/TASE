from aioarango.errors.base import ArangoServerError


class AQLQueryKillError(ArangoServerError):
    """Failed to kill the query."""
