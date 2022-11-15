from aioarango.errors.server import ArangoServerError


class ClusterServerEngineError(ArangoServerError):
    """Failed to retrieve server node engine."""
