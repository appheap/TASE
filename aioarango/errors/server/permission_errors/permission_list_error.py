from aioarango.errors.server import ArangoServerError


class PermissionListError(ArangoServerError):
    """Failed to list user permissions."""
