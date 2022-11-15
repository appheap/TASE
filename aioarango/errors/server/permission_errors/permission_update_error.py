from aioarango.errors.base import ArangoServerError


class PermissionUpdateError(ArangoServerError):
    """Failed to update user permission."""
