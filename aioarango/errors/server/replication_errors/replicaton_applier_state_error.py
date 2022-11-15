from aioarango.errors.server import ArangoServerError


class ReplicationApplierStateError(ArangoServerError):
    """Failed to retrieve replication applier state."""
