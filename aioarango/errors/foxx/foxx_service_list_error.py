from aioarango.errors.base import ArangoServerError


class FoxxServiceListError(ArangoServerError):
    """Failed to retrieve Foxx services."""
