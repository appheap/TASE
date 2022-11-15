from aioarango.errors.server import ArangoServerError


class UserDeleteError(ArangoServerError):
    """Failed to delete user."""
