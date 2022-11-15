from aioarango.errors.client import ArangoClientError


class BatchJobResultError(ArangoClientError):
    """Failed to retrieve batch job result."""
