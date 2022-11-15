from aioarango.errors.server import ArangoServerError


class DocumentDeleteError(ArangoServerError):
    """Failed to delete document."""
