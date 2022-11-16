from aioarango.errors.base import ArangoServerError


class ReplicationSyncError(ArangoServerError):
    """Failed to synchronize data from remote."""
