from aioarango.errors.server import ArangoServerError


class TaskCreateError(ArangoServerError):
    """Failed to create server task."""
