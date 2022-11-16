from aioarango.errors.base import ArangoServerError


class ClusterMaintenanceModeError(ArangoServerError):
    """Failed to enable/disable cluster supervision maintenance mode."""
