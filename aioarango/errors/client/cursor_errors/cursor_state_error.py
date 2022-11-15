from aioarango.errors.client import ArangoClientError


class CursorStateError(ArangoClientError):
    """The cursor object was in a bad state."""
