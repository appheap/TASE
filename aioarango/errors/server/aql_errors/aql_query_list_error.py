from aioarango.errors.base import ArangoServerError


class AQLQueryListError(ArangoServerError):
    """Failed to retrieve running AQL queries."""
