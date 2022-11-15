from aioarango.errors.server import ArangoServerError


class EdgeDefinitionCreateError(ArangoServerError):
    """Failed to create edge definition."""
