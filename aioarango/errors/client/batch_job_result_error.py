from .arango_client_error import ArangoClientError


class BatchJobResultError(ArangoClientError):
    """Failed to retrieve batch job result."""
