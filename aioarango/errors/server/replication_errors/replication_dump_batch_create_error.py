from aioarango.errors.base import ArangoServerError


class ReplicationDumpBatchCreateError(ArangoServerError):
    """Failed to create dump batch."""
