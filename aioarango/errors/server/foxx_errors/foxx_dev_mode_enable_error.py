from aioarango.errors.server import ArangoServerError


class FoxxDevModeEnableError(ArangoServerError):
    """Failed to enable development mode for Foxx service."""
