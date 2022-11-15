from aioarango.errors.server import ArangoServerError


class ViewListError(ArangoServerError):
    """Failed to retrieve views."""
