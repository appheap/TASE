from aioarango.errors.base import ArangoServerError


class DocumentUniqueConstraintError(ArangoServerError):
    """Document with the same qualifiers in an indexed attribute conflicts with an already existing document and thus violates that unique constraint."""
