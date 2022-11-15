from aioarango.errors.base import ArangoServerError


class FoxxServiceReplaceError(ArangoServerError):
    """Failed to replace Foxx service."""
