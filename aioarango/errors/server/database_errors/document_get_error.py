from aioarango.errors.server import ArangoServerError


class DocumentGetError(ArangoServerError):
    """Failed to retrieve document."""
