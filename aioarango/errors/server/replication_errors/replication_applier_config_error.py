from aioarango.errors.server import ArangoServerError


class ReplicationApplierConfigError(ArangoServerError):
    """Failed to retrieve replication applier configuration."""
