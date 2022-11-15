from aioarango.errors.server import ArangoServerError


class ReplicationSyncError(ArangoServerError):
    """Failed to synchronize data from remote."""
