from aioarango.errors.server import ArangoServerError


class AnalyzerGetError(ArangoServerError):
    """Failed to retrieve analyzer details."""
