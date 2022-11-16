from aioarango.errors.base import ArangoServerError


class ViewCreateError(ArangoServerError):
    """Failed to create view."""
