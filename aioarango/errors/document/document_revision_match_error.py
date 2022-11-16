from aioarango.errors.base import ArangoServerError


class DocumentRevisionMatchError(ArangoServerError):
    """The expected and actual document revisions matched."""
