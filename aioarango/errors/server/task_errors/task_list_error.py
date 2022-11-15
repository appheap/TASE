from aioarango.errors.server import ArangoServerError


class TaskListError(ArangoServerError):
    """Failed to retrieve server tasks."""
