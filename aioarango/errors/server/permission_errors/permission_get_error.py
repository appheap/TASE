from aioarango.errors.server import ArangoServerError


class PermissionGetError(ArangoServerError):
    """Failed to retrieve user permission."""
