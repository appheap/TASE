from aioarango.errors.base import ArangoServerError


class TaskDeleteError(ArangoServerError):
    """Failed to delete server task."""
