from aioarango.errors.server import ArangoServerError


class GraphListError(ArangoServerError):
    """Failed to retrieve graphs."""
