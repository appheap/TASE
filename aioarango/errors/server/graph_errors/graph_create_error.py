from aioarango.errors.base import ArangoServerError


class GraphCreateError(ArangoServerError):
    """Failed to create the graph."""
