from aioarango.errors.base import ArangoClientError


class ServerConnectionError(ArangoClientError):
    """Failed to connect to ArangoDB server."""
