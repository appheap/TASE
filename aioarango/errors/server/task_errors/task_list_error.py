from aioarango.errors.base import ArangoServerError


class TaskListError(ArangoServerError):
    """Failed to retrieve server tasks."""
