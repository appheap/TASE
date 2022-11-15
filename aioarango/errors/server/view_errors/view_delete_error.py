from aioarango.errors.server import ArangoServerError


class ViewDeleteError(ArangoServerError):
    """Failed to delete view."""
