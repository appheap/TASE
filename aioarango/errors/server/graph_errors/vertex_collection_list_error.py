from aioarango.errors.server import ArangoServerError


class VertexCollectionListError(ArangoServerError):
    """Failed to retrieve vertex collections."""
