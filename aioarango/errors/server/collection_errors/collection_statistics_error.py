from aioarango.errors.base import ArangoServerError


class CollectionStatisticsError(ArangoServerError):
    """Failed to retrieve collection statistics."""
