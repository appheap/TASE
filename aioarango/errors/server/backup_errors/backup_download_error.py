from aioarango.errors.server import ArangoServerError


class BackupDownloadError(ArangoServerError):
    """Failed to download a backup from remote repository."""
