from aioarango.errors.base import ArangoServerError


class IndexLoadError(ArangoServerError):
    """Failed to load indexes into memory."""
