from aioarango.errors.server import ArangoServerError


class ReplicationLoggerStateError(ArangoServerError):
    """Failed to retrieve logger state."""
