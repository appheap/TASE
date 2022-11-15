from aioarango.errors.server import ArangoServerError


class AQLQueryValidateError(ArangoServerError):
    """Failed to parse and validate query."""
