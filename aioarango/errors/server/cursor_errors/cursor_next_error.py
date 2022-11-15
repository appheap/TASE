from aioarango.errors.server import ArangoServerError


class CursorNextError(ArangoServerError):
    """Failed to retrieve the next result batch from server."""
