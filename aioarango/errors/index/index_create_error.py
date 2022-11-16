from aioarango.errors.base import ArangoServerError


class IndexCreateError(ArangoServerError):
    """Failed to create collection index."""
