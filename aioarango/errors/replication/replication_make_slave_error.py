from aioarango.errors.base import ArangoServerError


class ReplicationMakeSlaveError(ArangoServerError):
    """Failed to change role to slave."""
