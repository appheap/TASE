from aioarango.errors.base import ArangoServerError


class FoxxTestRunError(ArangoServerError):
    """Failed to run Foxx service tests."""
