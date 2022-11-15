from aioarango.errors.server import ArangoServerError


class DocumentInsertError(ArangoServerError):
    """Failed to insert document."""
