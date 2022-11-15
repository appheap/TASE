from aioarango.errors.client import ArangoClientError


class CursorEmptyError(ArangoClientError):
    """The current batch in cursor was empty."""
