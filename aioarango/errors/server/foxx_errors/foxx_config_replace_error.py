from aioarango.errors.base import ArangoServerError


class FoxxConfigReplaceError(ArangoServerError):
    """Failed to replace Foxx service configuration."""
