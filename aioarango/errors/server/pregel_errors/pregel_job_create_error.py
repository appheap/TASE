from aioarango.errors.base import ArangoServerError


class PregelJobCreateError(ArangoServerError):
    """Failed to create Pregel job."""
