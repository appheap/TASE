from aioarango.errors.base import ArangoServerError


class FoxxDependencyReplaceError(ArangoServerError):
    """Failed to replace Foxx service dependencies."""
