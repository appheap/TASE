from aioarango.errors.server import ArangoServerError


class CollectionPropertiesError(ArangoServerError):
    """Failed to retrieve collection properties."""
