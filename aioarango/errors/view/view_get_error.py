from aioarango.errors.base import ArangoServerError


class ViewGetError(ArangoServerError):
    """Failed to retrieve view details."""
