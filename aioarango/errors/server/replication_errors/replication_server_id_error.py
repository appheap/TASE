from aioarango.errors.server import ArangoServerError


class ReplicationServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""
