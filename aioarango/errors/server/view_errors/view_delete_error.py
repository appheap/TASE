from aioarango.errors.base import ArangoServerError


class ViewDeleteError(ArangoServerError):
    """Failed to delete view."""
