from aioarango.errors.base import ArangoServerError


class ServerTLSReloadError(ArangoServerError):
    """Failed to reload TLS."""
