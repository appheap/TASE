from aioarango.errors.base import ArangoServerError


class UserReplaceError(ArangoServerError):
    """Failed to replace user."""
