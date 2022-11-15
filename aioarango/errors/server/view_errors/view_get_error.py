from aioarango.errors.server import ArangoServerError


class ViewGetError(ArangoServerError):
    """Failed to retrieve view details."""
