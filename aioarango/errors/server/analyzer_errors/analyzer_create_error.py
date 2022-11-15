from aioarango.errors.base import ArangoServerError


class AnalyzerCreateError(ArangoServerError):
    """Failed to create analyzer."""
