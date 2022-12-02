from .arango_client_error import ArangoClientError


class CursorCountError(ArangoClientError, TypeError):
    """The cursor count was not enabled."""
