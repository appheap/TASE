from aioarango.errors.server import ArangoServerError


class DocumentKeysError(ArangoServerError):
    """Failed to retrieve document keys."""
