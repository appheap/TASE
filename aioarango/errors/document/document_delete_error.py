from aioarango.errors.base import ArangoServerError


class DocumentDeleteError(ArangoServerError):
    """Failed to delete document."""
