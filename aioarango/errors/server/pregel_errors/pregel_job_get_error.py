from aioarango.errors.base import ArangoServerError


class PregelJobGetError(ArangoServerError):
    """Failed to retrieve Pregel job details."""
