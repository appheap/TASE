from aioarango.errors.server import ArangoServerError


class UserGetError(ArangoServerError):
    """Failed to retrieve user details."""
