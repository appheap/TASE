from aioarango.errors.server import ArangoServerError


class PermissionResetError(ArangoServerError):
    """Failed to reset user permission."""
