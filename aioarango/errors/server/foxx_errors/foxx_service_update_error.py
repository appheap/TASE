from aioarango.errors.base import ArangoServerError


class FoxxServiceUpdateError(ArangoServerError):
    """Failed to update Foxx service."""
