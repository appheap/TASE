from aioarango.errors.server import ArangoServerError


class FoxxTestRunError(ArangoServerError):
    """Failed to run Foxx service tests."""
