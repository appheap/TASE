from aioarango.errors.server import ArangoServerError


class ServerRequiredDBVersionError(ArangoServerError):
    """Failed to retrieve server target version."""
