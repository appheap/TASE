from aioarango.errors.base import ArangoServerError


class ReplicationLoggerStateError(ArangoServerError):
    """Failed to retrieve logger state."""
