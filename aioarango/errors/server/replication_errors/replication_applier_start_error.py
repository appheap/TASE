from aioarango.errors.server import ArangoServerError


class ReplicationApplierStartError(ArangoServerError):
    """Failed to start replication applier."""
