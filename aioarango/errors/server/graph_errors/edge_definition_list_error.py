from aioarango.errors.server import ArangoServerError


class EdgeDefinitionListError(ArangoServerError):
    """Failed to retrieve edge definitions."""
