from aioarango.errors.server import ArangoServerError


class FoxxServiceUpdateError(ArangoServerError):
    """Failed to update Foxx service."""
