from aioarango.errors.base import ArangoServerError


class DocumentRevisionMisMatchError(ArangoServerError):
    """The expected and actual document revisions mismatched."""
