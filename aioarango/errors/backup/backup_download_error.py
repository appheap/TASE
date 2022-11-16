from aioarango.errors.base import ArangoServerError


class BackupDownloadError(ArangoServerError):
    """Failed to download a backup from remote repository."""
