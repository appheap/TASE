from aioarango.errors.base import ArangoServerError


class FoxxReadmeGetError(ArangoServerError):
    """Failed to retrieve Foxx service readme."""
