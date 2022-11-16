from aioarango.errors.base import ArangoServerError


class DocumentGetError(ArangoServerError):
    """Failed to retrieve document."""
