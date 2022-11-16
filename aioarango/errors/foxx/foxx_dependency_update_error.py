from aioarango.errors.base import ArangoServerError


class FoxxDependencyUpdateError(ArangoServerError):
    """Failed to update Foxx service dependencies."""
