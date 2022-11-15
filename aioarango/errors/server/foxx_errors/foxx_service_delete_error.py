from aioarango.errors.base import ArangoServerError


class FoxxServiceDeleteError(ArangoServerError):
    """Failed to delete Foxx services."""
