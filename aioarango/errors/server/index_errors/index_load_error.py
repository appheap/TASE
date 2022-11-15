from aioarango.errors.server import ArangoServerError


class IndexLoadError(ArangoServerError):
    """Failed to load indexes into memory."""
