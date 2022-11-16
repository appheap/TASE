from aioarango.errors.base import ArangoServerError


class CollectionPropertiesError(ArangoServerError):
    """Failed to retrieve collection properties."""
