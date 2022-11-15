from aioarango.errors.base import ArangoServerError


class AQLFunctionCreateError(ArangoServerError):
    """Failed to create AQL user function."""
