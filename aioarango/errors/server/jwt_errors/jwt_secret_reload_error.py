from aioarango.errors.server import ArangoServerError


class JWTSecretReloadError(ArangoServerError):
    """Failed to reload JWT secrets."""
