from aioarango.errors.base import ArangoServerError


class ServerEngineError(ArangoServerError):
    """Failed to retrieve database engine."""
