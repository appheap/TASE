from aioarango.errors.base import ArangoServerError


class CollectionResponsibleShardError(ArangoServerError):
    """Failed to retrieve responsible shard."""
