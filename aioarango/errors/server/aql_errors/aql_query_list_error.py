from aioarango.errors.server import ArangoServerError


class AQLQueryListError(ArangoServerError):
    """Failed to retrieve running AQL queries."""
