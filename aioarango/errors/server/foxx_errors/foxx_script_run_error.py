from aioarango.errors.server import ArangoServerError


class FoxxScriptRunError(ArangoServerError):
    """Failed to run Foxx service script."""
