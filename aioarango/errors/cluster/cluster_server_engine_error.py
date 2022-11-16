from aioarango.errors.base import ArangoServerError


class ClusterServerEngineError(ArangoServerError):
    """Failed to retrieve server node engine."""
