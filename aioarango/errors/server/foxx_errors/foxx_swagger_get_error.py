from aioarango.errors.server import ArangoServerError


class FoxxSwaggerGetError(ArangoServerError):
    """Failed to retrieve Foxx service swagger."""
