from aioarango.errors.server import ArangoServerError


class AnalyzerCreateError(ArangoServerError):
    """Failed to create analyzer."""
