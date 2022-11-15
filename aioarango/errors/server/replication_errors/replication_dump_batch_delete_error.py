from aioarango.errors.server import ArangoServerError


class ReplicationDumpBatchDeleteError(ArangoServerError):
    """Failed to delete a dump batch."""
