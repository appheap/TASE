from aioarango.errors.server import ArangoServerError


class ViewUpdateError(ArangoServerError):
    """Failed to update view."""
