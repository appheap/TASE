from aioarango.errors.server import ArangoServerError


class AQLFunctionListError(ArangoServerError):
    """Failed to retrieve AQL user functions."""
