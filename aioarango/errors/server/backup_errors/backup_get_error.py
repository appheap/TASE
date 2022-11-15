from aioarango.errors.base import ArangoServerError


class BackupGetError(ArangoServerError):
    """Failed to retrieve backup details."""
