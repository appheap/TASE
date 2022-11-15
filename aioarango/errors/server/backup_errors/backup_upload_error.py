from aioarango.errors.server import ArangoServerError


class BackupUploadError(ArangoServerError):
    """Failed to upload a backup to remote repository."""
