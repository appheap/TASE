from aioarango.errors.server import ArangoServerError


class FoxxScriptListError(ArangoServerError):
    """Failed to retrieve Foxx service scripts."""
