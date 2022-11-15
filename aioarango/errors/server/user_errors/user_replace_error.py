from aioarango.errors.server import ArangoServerError


class UserReplaceError(ArangoServerError):
    """Failed to replace user."""
