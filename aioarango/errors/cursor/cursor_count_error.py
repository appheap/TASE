from aioarango.errors.base import ArangoClientError


class CursorCountError(ArangoClientError, TypeError):
    """The cursor count was not enabled."""
