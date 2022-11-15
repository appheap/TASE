from aioarango.errors.server import ArangoServerError


class GraphCreateError(ArangoServerError):
    """Failed to create the graph."""
