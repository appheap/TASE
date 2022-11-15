from aioarango.errors.server import ArangoServerError


class AQLFunctionDeleteError(ArangoServerError):
    """Failed to delete AQL user function."""
