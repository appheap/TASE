from aioarango.errors.server import ArangoServerError


class ReplicationDumpBatchCreateError(ArangoServerError):
    """Failed to create dump batch."""
