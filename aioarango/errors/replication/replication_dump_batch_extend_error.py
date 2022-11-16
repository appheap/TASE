from aioarango.errors.base import ArangoServerError


class ReplicationDumpBatchExtendError(ArangoServerError):
    """Failed to extend a dump batch."""
