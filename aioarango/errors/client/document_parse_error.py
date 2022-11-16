from .arango_client_error import ArangoClientError


class DocumentParseError(ArangoClientError):
    """Failed to parse document input."""
