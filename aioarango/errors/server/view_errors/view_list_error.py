from aioarango.errors.base import ArangoServerError


class ViewListError(ArangoServerError):
    """Failed to retrieve views."""
