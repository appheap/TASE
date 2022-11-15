from aioarango.errors.base import ArangoServerError


class DocumentIllegalError(ArangoServerError):
    """Document is illegal."""
