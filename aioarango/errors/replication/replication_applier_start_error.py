from aioarango.errors.base import ArangoServerError


class ReplicationApplierStartError(ArangoServerError):
    """Failed to start replication applier."""
