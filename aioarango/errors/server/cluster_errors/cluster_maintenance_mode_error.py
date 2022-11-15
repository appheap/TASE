from aioarango.errors.server import ArangoServerError


class ClusterMaintenanceModeError(ArangoServerError):
    """Failed to enable/disable cluster supervision maintenance mode."""
