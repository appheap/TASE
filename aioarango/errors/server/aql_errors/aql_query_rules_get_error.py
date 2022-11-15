from aioarango.errors.server import ArangoServerError


class AQLQueryRulesGetError(ArangoServerError):
    """Failed to retrieve AQL query rules."""
