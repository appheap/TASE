from aioarango.errors.server import ArangoServerError


class DocumentUpdateError(ArangoServerError):
    """Failed to update document."""
