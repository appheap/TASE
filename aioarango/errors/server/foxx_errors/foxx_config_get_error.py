from aioarango.errors.base import ArangoServerError


class FoxxConfigGetError(ArangoServerError):
    """Failed to retrieve Foxx service configuration."""
