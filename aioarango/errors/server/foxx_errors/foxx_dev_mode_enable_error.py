from aioarango.errors.base import ArangoServerError


class FoxxDevModeEnableError(ArangoServerError):
    """Failed to enable development mode for Foxx service."""
