from aioarango.errors.base import ArangoServerError


class FoxxScriptListError(ArangoServerError):
    """Failed to retrieve Foxx service scripts."""
