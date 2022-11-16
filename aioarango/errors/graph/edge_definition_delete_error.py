from aioarango.errors.base import ArangoServerError


class EdgeDefinitionDeleteError(ArangoServerError):
    """Failed to delete edge definition."""
