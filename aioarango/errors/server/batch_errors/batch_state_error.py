from aioarango.errors.client import ArangoClientError


class BatchStateError(ArangoClientError):
    """The batch object was in a bad state."""
