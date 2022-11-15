from aioarango.errors.base import ArangoServerError


class DocumentRevisionError(ArangoServerError):
    """The expected and actual document revisions mismatched."""
