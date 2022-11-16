from aioarango.errors.base import ArangoServerError


class FoxxServiceGetError(ArangoServerError):
    """Failed to retrieve Foxx service metadata."""
