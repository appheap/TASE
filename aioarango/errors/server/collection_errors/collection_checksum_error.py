from aioarango.errors.base import ArangoServerError


class CollectionChecksumError(ArangoServerError):
    """Failed to retrieve collection checksum."""
