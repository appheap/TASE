from aioarango.errors.server import ArangoServerError


class ViewRenameError(ArangoServerError):
    """Failed to rename view."""
