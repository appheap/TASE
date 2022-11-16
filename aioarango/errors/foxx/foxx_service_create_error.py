from aioarango.errors.base import ArangoServerError


class FoxxServiceCreateError(ArangoServerError):
    """Failed to create Foxx service."""
