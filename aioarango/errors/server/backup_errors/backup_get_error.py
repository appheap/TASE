from aioarango.errors.server import ArangoServerError


class BackupGetError(ArangoServerError):
    """Failed to retrieve backup details."""
