from aioarango.errors.base import ArangoServerError


class DocumentIDsError(ArangoServerError):
    """Failed to retrieve document IDs."""
