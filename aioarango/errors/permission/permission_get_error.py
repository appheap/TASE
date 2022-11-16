from aioarango.errors.base import ArangoServerError


class PermissionGetError(ArangoServerError):
    """Failed to retrieve user permission."""
