from aioarango.errors.base import ArangoServerError


class DocumentCountError(ArangoServerError):
    """Failed to retrieve document count."""
