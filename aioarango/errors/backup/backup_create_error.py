from aioarango.errors.base import ArangoServerError


class BackupCreateError(ArangoServerError):
    """Failed to create a backup."""
