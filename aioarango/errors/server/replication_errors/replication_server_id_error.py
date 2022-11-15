from aioarango.errors.base import ArangoServerError


class ReplicationServerIDError(ArangoServerError):
    """Failed to retrieve server ID."""
