from aioarango.errors.server import ArangoServerError


class CursorCloseError(ArangoServerError):
    """Failed to delete the cursor result from server."""
