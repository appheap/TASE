from aioarango.errors.server import ArangoServerError


class ViewCreateError(ArangoServerError):
    """Failed to create view."""
