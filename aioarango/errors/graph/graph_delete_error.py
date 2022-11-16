from aioarango.errors.base import ArangoServerError


class GraphDeleteError(ArangoServerError):
    """Failed to delete the graph."""
