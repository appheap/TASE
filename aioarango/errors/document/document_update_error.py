from aioarango.errors.base import ArangoServerError


class DocumentUpdateError(ArangoServerError):
    """Failed to update document."""
