from aioarango.errors.base import ArangoServerError


class UserCreateError(ArangoServerError):
    """Failed to create user."""
