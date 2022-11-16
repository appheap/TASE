from .arango_client_error import ArangoClientError


class BatchStateError(ArangoClientError):
    """The batch object was in a bad state."""
