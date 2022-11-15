from aioarango.errors.base import ArangoServerError


class EdgeDefinitionCreateError(ArangoServerError):
    """Failed to create edge definition."""
