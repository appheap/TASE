from aioarango.errors.server import ArangoServerError


class EdgeListError(ArangoServerError):
    """Failed to retrieve edges coming in and out of a vertex."""
