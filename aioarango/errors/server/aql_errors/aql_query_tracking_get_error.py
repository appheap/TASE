from aioarango.errors.server import ArangoServerError


class AQLQueryTrackingGetError(ArangoServerError):
    """Failed to retrieve AQL tracking properties."""
