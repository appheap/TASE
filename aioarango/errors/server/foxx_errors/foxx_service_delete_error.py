from aioarango.errors.server import ArangoServerError


class FoxxServiceDeleteError(ArangoServerError):
    """Failed to delete Foxx services."""
