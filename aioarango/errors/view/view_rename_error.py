from aioarango.errors.base import ArangoServerError


class ViewRenameError(ArangoServerError):
    """Failed to rename view."""
