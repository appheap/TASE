from aioarango.errors.base import ArangoServerError


class FoxxScriptRunError(ArangoServerError):
    """Failed to run Foxx service script."""
