from aioarango.errors.base import ArangoServerError


class ReplicationDumpBatchDeleteError(ArangoServerError):
    """Failed to delete a dump batch."""
