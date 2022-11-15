from aioarango.errors.base import ArangoServerError


class DocumentInsertError(ArangoServerError):
    """Failed to insert document."""
