from aioarango.errors.base import ArangoClientError


class CursorEmptyError(ArangoClientError):
    """The current batch in cursor was empty."""
