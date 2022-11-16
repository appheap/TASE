from aioarango.errors.base import ArangoServerError


class FoxxConfigUpdateError(ArangoServerError):
    """Failed to update Foxx service configuration."""
