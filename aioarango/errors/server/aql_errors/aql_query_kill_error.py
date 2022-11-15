from aioarango.errors.server import ArangoServerError


class AQLQueryKillError(ArangoServerError):
    """Failed to kill the query."""
