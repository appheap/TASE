from .arango_client_error import ArangoClientError


class CursorStateError(ArangoClientError):
    """The cursor object was in a bad state."""
