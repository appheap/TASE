from aioarango.errors.base import ArangoServerError


class AQLFunctionListError(ArangoServerError):
    """Failed to retrieve AQL user functions."""
