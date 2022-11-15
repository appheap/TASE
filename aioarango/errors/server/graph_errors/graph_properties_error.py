from aioarango.errors.base import ArangoServerError


class GraphPropertiesError(ArangoServerError):
    """Failed to retrieve graph properties."""
