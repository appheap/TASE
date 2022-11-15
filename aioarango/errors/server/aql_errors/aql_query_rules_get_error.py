from aioarango.errors.base import ArangoServerError


class AQLQueryRulesGetError(ArangoServerError):
    """Failed to retrieve AQL query rules."""
