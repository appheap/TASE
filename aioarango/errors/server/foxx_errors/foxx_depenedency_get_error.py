from aioarango.errors.server import ArangoServerError


class FoxxDependencyGetError(ArangoServerError):
    """Failed to retrieve Foxx service dependencies."""
