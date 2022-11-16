from aioarango.errors.base import ArangoServerError


class UserListError(ArangoServerError):
    """Failed to retrieve users."""
