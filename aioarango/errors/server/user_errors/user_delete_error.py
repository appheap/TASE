from aioarango.errors.base import ArangoServerError


class UserDeleteError(ArangoServerError):
    """Failed to delete user."""
