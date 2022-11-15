from aioarango.errors.base import ArangoServerError


class JWTSecretListError(ArangoServerError):
    """Failed to retrieve information on currently loaded JWT secrets."""
