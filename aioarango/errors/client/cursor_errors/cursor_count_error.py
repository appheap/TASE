from aioarango.errors.client import ArangoClientError


class CursorCountError(ArangoClientError, TypeError):
    """The cursor count was not enabled."""
