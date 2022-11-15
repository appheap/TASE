from aioarango.errors.client import ArangoClientError


class DocumentParseError(ArangoClientError):
    """Failed to parse document input."""
