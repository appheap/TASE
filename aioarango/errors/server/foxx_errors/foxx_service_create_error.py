from aioarango.errors.server import ArangoServerError


class FoxxServiceCreateError(ArangoServerError):
    """Failed to create Foxx service."""
