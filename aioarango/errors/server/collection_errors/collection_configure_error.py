from aioarango.errors.server import ArangoServerError


class CollectionConfigureError(ArangoServerError):
    """Failed to configure collection properties."""
