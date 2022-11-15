from aioarango.errors.server import ArangoServerError


class CollectionStatisticsError(ArangoServerError):
    """Failed to retrieve collection statistics."""
