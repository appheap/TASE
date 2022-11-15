from aioarango.errors.base import ArangoServerError


class AQLQueryValidateError(ArangoServerError):
    """Failed to parse and validate query."""
