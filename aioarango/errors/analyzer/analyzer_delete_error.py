from aioarango.errors.base import ArangoServerError


class AnalyzerDeleteError(ArangoServerError):
    """Failed to delete analyzer."""
