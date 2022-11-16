from aioarango.errors.base import ArangoServerError


class PermissionListError(ArangoServerError):
    """Failed to list user permissions."""
