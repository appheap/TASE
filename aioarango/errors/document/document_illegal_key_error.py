from aioarango.errors.base import ArangoServerError


class DocumentIllegalKeyError(ArangoServerError):
    """Document key is illegal."""
