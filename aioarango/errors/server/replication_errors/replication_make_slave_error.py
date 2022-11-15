from aioarango.errors.server import ArangoServerError


class ReplicationMakeSlaveError(ArangoServerError):
    """Failed to change role to slave."""
