from aioarango.errors.server import ArangoServerError


class PregelJobDeleteError(ArangoServerError):
    """Failed to delete Pregel job."""
