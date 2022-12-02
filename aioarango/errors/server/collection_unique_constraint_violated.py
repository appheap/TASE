from aioarango.errors import ArangoServerError


class CollectionUniqueConstraintViolated(ArangoServerError):
    """
    Document with the same qualifiers in an indexed attribute conflicts with an already
    existing document and thus violates that unique constraint.
    """
