from aioarango.errors.server import ArangoServerError


class GraphPropertiesError(ArangoServerError):
    """Failed to retrieve graph properties."""
