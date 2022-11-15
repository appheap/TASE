from aioarango.errors.base import ArangoServerError


class JWTAuthError(ArangoServerError):
    """Failed to get a new JWT token from ArangoDB."""
