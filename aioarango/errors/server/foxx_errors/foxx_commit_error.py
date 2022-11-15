from aioarango.errors.base import ArangoServerError


class FoxxCommitError(ArangoServerError):
    """Failed to commit local Foxx service state."""
