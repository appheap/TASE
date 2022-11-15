from aioarango.errors.base import ArangoServerError


class EdgeListError(ArangoServerError):
    """Failed to retrieve edges coming in and out of a vertex."""
