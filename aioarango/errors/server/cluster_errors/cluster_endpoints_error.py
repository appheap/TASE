from aioarango.errors.base import ArangoServerError


class ClusterEndpointsError(ArangoServerError):
    """Failed to retrieve cluster endpoints."""
