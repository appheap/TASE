from aioarango.errors.base import ArangoServerError


class PermissionResetError(ArangoServerError):
    """Failed to reset user permission."""
