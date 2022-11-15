from aioarango.errors.server import ArangoServerError


class ReplicationApplierConfigSetError(ArangoServerError):
    """Failed to update replication applier configuration."""
