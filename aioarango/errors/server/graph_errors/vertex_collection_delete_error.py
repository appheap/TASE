from aioarango.errors.base import ArangoServerError


class VertexCollectionDeleteError(ArangoServerError):
    """Failed to delete vertex collection."""
