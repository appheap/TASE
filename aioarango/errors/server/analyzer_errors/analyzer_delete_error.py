from aioarango.errors.server import ArangoServerError


class AnalyzerDeleteError(ArangoServerError):
    """Failed to delete analyzer."""
