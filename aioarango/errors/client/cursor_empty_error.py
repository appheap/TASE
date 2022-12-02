from .arango_client_error import ArangoClientError


class CursorEmptyError(ArangoClientError):
    """The current batch in cursor was empty."""
