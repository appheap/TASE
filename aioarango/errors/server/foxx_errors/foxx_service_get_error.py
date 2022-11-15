from aioarango.errors.server import ArangoServerError


class FoxxServiceGetError(ArangoServerError):
    """Failed to retrieve Foxx service metadata."""
