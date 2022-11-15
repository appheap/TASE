from aioarango.errors.server import ArangoServerError


class PregelJobCreateError(ArangoServerError):
    """Failed to create Pregel job."""
