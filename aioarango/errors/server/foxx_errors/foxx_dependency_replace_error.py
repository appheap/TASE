from aioarango.errors.server import ArangoServerError


class FoxxDependencyReplaceError(ArangoServerError):
    """Failed to replace Foxx service dependencies."""
