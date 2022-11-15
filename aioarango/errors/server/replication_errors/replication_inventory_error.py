from aioarango.errors.server import ArangoServerError


class ReplicationInventoryError(ArangoServerError):
    """Failed to retrieve inventory of collection and indexes."""
