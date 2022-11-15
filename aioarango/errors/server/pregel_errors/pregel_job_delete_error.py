from aioarango.errors.base import ArangoServerError


class PregelJobDeleteError(ArangoServerError):
    """Failed to delete Pregel job."""
