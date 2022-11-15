from aioarango.errors.server import ArangoServerError


class BackupDeleteError(ArangoServerError):
    """Failed to delete a backup."""
