from aioarango.errors.base import ArangoServerError


class GraphListError(ArangoServerError):
    """Failed to retrieve graphs."""
