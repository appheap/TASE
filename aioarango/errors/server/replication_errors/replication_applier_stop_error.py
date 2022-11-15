from aioarango.errors.server import ArangoServerError


class ReplicationApplierStopError(ArangoServerError):
    """Failed to stop replication applier."""
