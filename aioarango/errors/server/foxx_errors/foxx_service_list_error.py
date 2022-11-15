from aioarango.errors.server import ArangoServerError


class FoxxServiceListError(ArangoServerError):
    """Failed to retrieve Foxx services."""
