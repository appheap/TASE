from aioarango.errors.base import ArangoServerError


class ReplicationApplierConfigError(ArangoServerError):
    """Failed to retrieve replication applier configuration."""
