from aioarango.errors.base import ArangoServerError


class ReplicationApplierConfigSetError(ArangoServerError):
    """Failed to update replication applier configuration."""
