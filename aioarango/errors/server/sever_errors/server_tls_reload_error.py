from aioarango.errors.server import ArangoServerError


class ServerTLSReloadError(ArangoServerError):
    """Failed to reload TLS."""
