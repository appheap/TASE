from aioarango.errors.base import ArangoServerError


class ServerTLSError(ArangoServerError):
    """Failed to retrieve TLS data."""
