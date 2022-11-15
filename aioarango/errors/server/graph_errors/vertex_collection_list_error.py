from aioarango.errors.base import ArangoServerError


class VertexCollectionListError(ArangoServerError):
    """Failed to retrieve vertex collections."""
