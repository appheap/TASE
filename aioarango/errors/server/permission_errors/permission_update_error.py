from aioarango.errors.server import ArangoServerError


class PermissionUpdateError(ArangoServerError):
    """Failed to update user permission."""
