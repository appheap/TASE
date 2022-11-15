from aioarango.errors.base import ArangoServerError


class ReplicationApplierStopError(ArangoServerError):
    """Failed to stop replication applier."""
