from aioarango.errors.base import ArangoServerError


class AnalyzerListError(ArangoServerError):
    """Failed to retrieve analyzers."""
