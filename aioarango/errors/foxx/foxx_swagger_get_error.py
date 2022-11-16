from aioarango.errors.base import ArangoServerError


class FoxxSwaggerGetError(ArangoServerError):
    """Failed to retrieve Foxx service swagger."""
