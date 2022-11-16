from aioarango.errors.base import ArangoServerError


class DocumentInError(ArangoServerError):
    """Failed to check whether document exists."""
