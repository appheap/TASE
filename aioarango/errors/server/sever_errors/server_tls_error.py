from aioarango.errors.server import ArangoServerError


class ServerTLSError(ArangoServerError):
    """Failed to retrieve TLS data."""
