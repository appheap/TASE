from .arango_client_error import ArangoClientError


class GraphParseError(ArangoClientError):
    """Failed to parse graph input."""
