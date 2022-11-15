from aioarango.errors.server import ArangoServerError


class ReplicationDumpBatchExtendError(ArangoServerError):
    """Failed to extend a dump batch."""
