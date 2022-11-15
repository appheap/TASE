from aioarango.errors.server import ArangoServerError


class FoxxReadmeGetError(ArangoServerError):
    """Failed to retrieve Foxx service readme."""
