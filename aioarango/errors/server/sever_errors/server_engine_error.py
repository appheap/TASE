from aioarango.errors.server import ArangoServerError


class ServerEngineError(ArangoServerError):
    """Failed to retrieve database engine."""
