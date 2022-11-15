from aioarango.errors.server import ArangoServerError


class FoxxCommitError(ArangoServerError):
    """Failed to commit local Foxx service state."""
