from aioarango.errors.base import ArangoServerError


class ServerEncryptionError(ArangoServerError):
    """Failed to reload user-defined encryption keys."""
