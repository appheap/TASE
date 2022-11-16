from aioarango.errors.base import ArangoServerError


class FoxxDependencyGetError(ArangoServerError):
    """Failed to retrieve Foxx service dependencies."""
