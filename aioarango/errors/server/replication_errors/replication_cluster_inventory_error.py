from aioarango.errors.base import ArangoServerError


class ReplicationClusterInventoryError(ArangoServerError):
    """Failed to retrieve overview of collection and indexes in a cluster."""
