from aioarango.errors.base import ArangoServerError


class TaskCreateError(ArangoServerError):
    """Failed to create server task."""
