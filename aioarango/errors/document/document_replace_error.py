from aioarango.errors.base import ArangoServerError


class DocumentReplaceError(ArangoServerError):
    """Failed to replace document."""
