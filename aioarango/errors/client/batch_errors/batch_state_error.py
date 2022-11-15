from aioarango.errors.base import ArangoClientError


class BatchStateError(ArangoClientError):
    """The batch object was in a bad state."""
