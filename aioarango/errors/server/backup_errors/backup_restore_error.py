from aioarango.errors.server import ArangoServerError


class BackupRestoreError(ArangoServerError):
    """Failed to restore from backup."""
