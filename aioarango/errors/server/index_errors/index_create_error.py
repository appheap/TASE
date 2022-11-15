from aioarango.errors.server import ArangoServerError


class IndexCreateError(ArangoServerError):
    """Failed to create collection index."""
