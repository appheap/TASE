from aioarango.errors.base import ArangoServerError


class GraphTraverseError(ArangoServerError):
    """Failed to execute graph traversal."""
