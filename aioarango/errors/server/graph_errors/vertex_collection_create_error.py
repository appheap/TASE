from aioarango.errors.server import ArangoServerError


class VertexCollectionCreateError(ArangoServerError):
    """Failed to create vertex collection."""
