from aioarango.errors.base import ArangoServerError


class CollectionRecalculateCountError(ArangoServerError):
    """Failed to recalculate document count."""
