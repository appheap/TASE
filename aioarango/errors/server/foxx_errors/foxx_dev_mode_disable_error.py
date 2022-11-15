from aioarango.errors.base import ArangoServerError


class FoxxDevModeDisableError(ArangoServerError):
    """Failed to disable development mode for Foxx service."""
