from aioarango.errors.server import ArangoServerError


class AQLQueryTrackingSetError(ArangoServerError):
    """Failed to configure AQL tracking properties."""
