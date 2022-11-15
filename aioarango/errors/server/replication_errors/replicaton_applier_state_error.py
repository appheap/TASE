from aioarango.errors.base import ArangoServerError


class ReplicationApplierStateError(ArangoServerError):
    """Failed to retrieve replication applier state."""
