from aioarango.errors.server import ArangoServerError


class UserCreateError(ArangoServerError):
    """Failed to create user."""
