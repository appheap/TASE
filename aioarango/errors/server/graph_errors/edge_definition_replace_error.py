from aioarango.errors.server import ArangoServerError


class EdgeDefinitionReplaceError(ArangoServerError):
    """Failed to replace edge definition."""
