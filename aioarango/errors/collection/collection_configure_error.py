from aioarango.errors.base import ArangoServerError


class CollectionConfigureError(ArangoServerError):
    """Failed to configure collection properties."""
