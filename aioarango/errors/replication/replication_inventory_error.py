from aioarango.errors.base import ArangoServerError


class ReplicationInventoryError(ArangoServerError):
    """Failed to retrieve inventory of collection and indexes."""
