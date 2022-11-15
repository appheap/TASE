from aioarango.errors.server import ArangoServerError


class PregelJobGetError(ArangoServerError):
    """Failed to retrieve Pregel job details."""
