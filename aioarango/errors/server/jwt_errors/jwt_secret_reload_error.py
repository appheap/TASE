from aioarango.errors.base import ArangoServerError


class JWTSecretReloadError(ArangoServerError):
    """Failed to reload JWT secrets."""
