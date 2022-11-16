from .arango_client_error import ArangoClientError


class ServerConnectionError(ArangoClientError):
    """Failed to connect to ArangoDB server."""
