from aioarango.errors.base import ArangoServerError


class ViewUpdateError(ArangoServerError):
    """Failed to update view."""
