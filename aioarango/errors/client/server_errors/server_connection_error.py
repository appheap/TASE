from aioarango.errors.client import ArangoClientError


class ServerConnectionError(ArangoClientError):
    """Failed to connect to ArangoDB server."""

