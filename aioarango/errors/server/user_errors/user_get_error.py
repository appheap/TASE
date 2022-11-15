from aioarango.errors.base import ArangoServerError


class UserGetError(ArangoServerError):
    """Failed to retrieve user details."""
