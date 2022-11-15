from aioarango.errors.server import ArangoServerError


class UserListError(ArangoServerError):
    """Failed to retrieve users."""
