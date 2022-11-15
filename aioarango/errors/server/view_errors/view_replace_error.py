from aioarango.errors.server import ArangoServerError


class ViewReplaceError(ArangoServerError):
    """Failed to replace view."""
