from aioarango.errors.base import ArangoServerError


class CollectionRenameError(ArangoServerError):
    """Failed to rename collection."""
