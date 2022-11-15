from aioarango.errors.server import ArangoServerError


class CollectionChecksumError(ArangoServerError):
    """Failed to retrieve collection checksum."""
