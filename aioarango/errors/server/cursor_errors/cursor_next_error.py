from aioarango.errors.base import ArangoServerError


class CursorNextError(ArangoServerError):
    """Failed to retrieve the next result batch from server."""
