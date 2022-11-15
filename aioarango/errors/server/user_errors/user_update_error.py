from aioarango.errors.server import ArangoServerError


class UserUpdateError(ArangoServerError):
    """Failed to update user."""
