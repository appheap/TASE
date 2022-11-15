from aioarango.errors.server import ArangoServerError


class FoxxConfigGetError(ArangoServerError):
    """Failed to retrieve Foxx service configuration."""
