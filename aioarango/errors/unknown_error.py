from aioarango.errors.base import ArangoServerError


class UnknownError(ArangoServerError):
    """Unknown error."""
