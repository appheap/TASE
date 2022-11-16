from aioarango.errors.base import ArangoServerError


class AQLQueryTrackingGetError(ArangoServerError):
    """Failed to retrieve AQL tracking properties."""
