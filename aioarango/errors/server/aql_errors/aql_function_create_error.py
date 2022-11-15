from aioarango.errors.server import ArangoServerError


class AQLFunctionCreateError(ArangoServerError):
    """Failed to create AQL user function."""
