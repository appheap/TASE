from aioarango.errors.base import ArangoServerError


class AnalyzerGetError(ArangoServerError):
    """Failed to retrieve analyzer details."""
