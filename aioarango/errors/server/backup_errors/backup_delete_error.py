from aioarango.errors.base import ArangoServerError


class BackupDeleteError(ArangoServerError):
    """Failed to delete a backup."""
