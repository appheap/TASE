from aioarango.errors.server import ArangoServerError


class DocumentReplaceError(ArangoServerError):
    """Failed to replace document."""
