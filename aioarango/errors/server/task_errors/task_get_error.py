from aioarango.errors.base import ArangoServerError


class TaskGetError(ArangoServerError):
    """Failed to retrieve server task details."""
