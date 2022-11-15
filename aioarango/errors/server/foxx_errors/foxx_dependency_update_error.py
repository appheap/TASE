from aioarango.errors.server import ArangoServerError


class FoxxDependencyUpdateError(ArangoServerError):
    """Failed to update Foxx service dependencies."""
