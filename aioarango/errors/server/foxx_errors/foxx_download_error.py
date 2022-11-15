from aioarango.errors.server import ArangoServerError


class FoxxDownloadError(ArangoServerError):
    """Failed to download Foxx service bundle."""
