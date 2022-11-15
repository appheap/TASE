from aioarango.errors.base import ArangoServerError


class BackupRestoreError(ArangoServerError):
    """Failed to restore from backup."""
