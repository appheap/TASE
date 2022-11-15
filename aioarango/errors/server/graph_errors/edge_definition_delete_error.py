from aioarango.errors.server import ArangoServerError


class EdgeDefinitionDeleteError(ArangoServerError):
    """Failed to delete edge definition."""
