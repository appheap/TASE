from aioarango.errors.base import ArangoServerError


class EdgeDefinitionReplaceError(ArangoServerError):
    """Failed to replace edge definition."""
