from aioarango.errors.base import ArangoServerError


class EdgeDefinitionListError(ArangoServerError):
    """Failed to retrieve edge definitions."""
