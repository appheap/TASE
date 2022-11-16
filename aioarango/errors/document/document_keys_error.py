from aioarango.errors.base import ArangoServerError


class DocumentKeysError(ArangoServerError):
    """Failed to retrieve document keys."""
