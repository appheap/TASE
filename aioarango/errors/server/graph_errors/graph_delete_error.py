from aioarango.errors.server import ArangoServerError


class GraphDeleteError(ArangoServerError):
    """Failed to delete the graph."""
