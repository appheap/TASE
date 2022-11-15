from aioarango.errors.server import ArangoServerError


class VertexCollectionDeleteError(ArangoServerError):
    """Failed to delete vertex collection."""
