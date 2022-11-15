from aioarango.errors.base import ArangoServerError


class VertexCollectionCreateError(ArangoServerError):
    """Failed to create vertex collection."""
