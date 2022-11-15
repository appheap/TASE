from aioarango.errors.server import ArangoServerError


class DocumentIDsError(ArangoServerError):
    """Failed to retrieve document IDs."""
