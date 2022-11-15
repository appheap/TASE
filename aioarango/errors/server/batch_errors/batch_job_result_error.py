from aioarango.errors.base import ArangoClientError


class BatchJobResultError(ArangoClientError):
    """Failed to retrieve batch job result."""
