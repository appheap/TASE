from aioarango.errors.server import ArangoServerError


class FoxxConfigReplaceError(ArangoServerError):
    """Failed to replace Foxx service configuration."""
