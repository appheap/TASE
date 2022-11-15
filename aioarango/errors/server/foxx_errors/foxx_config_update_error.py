from aioarango.errors.server import ArangoServerError


class FoxxConfigUpdateError(ArangoServerError):
    """Failed to update Foxx service configuration."""
