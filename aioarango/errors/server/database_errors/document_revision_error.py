from aioarango.errors.server import ArangoServerError


class DocumentRevisionError(ArangoServerError):
    """The expected and actual document revisions mismatched."""
