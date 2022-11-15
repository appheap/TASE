from aioarango.errors.base import ArangoServerError


class FoxxDownloadError(ArangoServerError):
    """Failed to download Foxx service bundle."""
