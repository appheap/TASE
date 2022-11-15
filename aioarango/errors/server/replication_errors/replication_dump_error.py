from aioarango.errors.server import ArangoServerError


class ReplicationDumpError(ArangoServerError):
    """Failed to retrieve collection content."""
