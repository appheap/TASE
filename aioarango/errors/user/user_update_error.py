from aioarango.errors.base import ArangoServerError


class UserUpdateError(ArangoServerError):
    """Failed to update user."""
