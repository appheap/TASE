from aioarango.errors.base import ArangoServerError


class ReplicationDumpError(ArangoServerError):
    """Failed to retrieve collection content."""
