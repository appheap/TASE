from aioarango.errors.base import ArangoServerError


class ServerRequiredDBVersionError(ArangoServerError):
    """Failed to retrieve server target version."""
