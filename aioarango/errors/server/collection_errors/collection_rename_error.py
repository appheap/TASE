from aioarango.errors.server import ArangoServerError


class CollectionRenameError(ArangoServerError):
    """Failed to rename collection."""
