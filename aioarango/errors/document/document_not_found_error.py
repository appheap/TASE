from aioarango.errors.base import ArangoServerError


class DocumentNotFoundError(ArangoServerError):
    """Document not found."""
