from aioarango.errors.server import ArangoServerError


class GraphTraverseError(ArangoServerError):
    """Failed to execute graph traversal."""
