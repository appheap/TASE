from aioarango.errors import ArangoServerError


class DocumentRevisionMatchError(ArangoServerError):
    """The expected and actual document revisions matched."""
