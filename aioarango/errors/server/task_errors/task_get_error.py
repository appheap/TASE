from aioarango.errors.server import ArangoServerError


class TaskGetError(ArangoServerError):
    """Failed to retrieve server task details."""
