from aioarango.errors.server import ArangoServerError


class BackupCreateError(ArangoServerError):
    """Failed to create a backup."""
