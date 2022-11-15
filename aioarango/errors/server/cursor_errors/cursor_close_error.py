from aioarango.errors.base import ArangoServerError


class CursorCloseError(ArangoServerError):
    """Failed to delete the cursor result from server."""
