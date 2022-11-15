from aioarango.errors.server import ArangoServerError


class DocumentCountError(ArangoServerError):
    """Failed to retrieve document count."""
