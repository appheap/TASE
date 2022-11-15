from aioarango.errors.server import ArangoServerError


class CollectionRecalculateCountError(ArangoServerError):
    """Failed to recalculate document count."""
