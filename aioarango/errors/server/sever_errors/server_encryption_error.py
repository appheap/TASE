from aioarango.errors.server import ArangoServerError


class ServerEncryptionError(ArangoServerError):
    """Failed to reload user-defined encryption keys."""
