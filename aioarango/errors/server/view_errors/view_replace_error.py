from aioarango.errors.base import ArangoServerError


class ViewReplaceError(ArangoServerError):
    """Failed to replace view."""
