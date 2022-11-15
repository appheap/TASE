from aioarango.errors.server import ArangoServerError


class ClusterEndpointsError(ArangoServerError):
    """Failed to retrieve cluster endpoints."""
