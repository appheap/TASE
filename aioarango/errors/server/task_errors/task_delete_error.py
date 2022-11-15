from aioarango.errors.server import ArangoServerError


class TaskDeleteError(ArangoServerError):
    """Failed to delete server task."""
