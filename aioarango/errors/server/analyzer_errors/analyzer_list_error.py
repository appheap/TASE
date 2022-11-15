from aioarango.errors.server import ArangoServerError


class AnalyzerListError(ArangoServerError):
    """Failed to retrieve analyzers."""
