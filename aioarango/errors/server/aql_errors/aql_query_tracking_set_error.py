from aioarango.errors.base import ArangoServerError


class AQLQueryTrackingSetError(ArangoServerError):
    """Failed to configure AQL tracking properties."""
