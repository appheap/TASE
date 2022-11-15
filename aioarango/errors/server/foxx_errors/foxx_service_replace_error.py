from aioarango.errors.server import ArangoServerError


class FoxxServiceReplaceError(ArangoServerError):
    """Failed to replace Foxx service."""
