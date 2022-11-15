from aioarango.errors.server import ArangoServerError


class CollectionResponsibleShardError(ArangoServerError):
    """Failed to retrieve responsible shard."""
