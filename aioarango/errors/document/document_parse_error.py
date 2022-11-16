from aioarango.errors.base import ArangoClientError


class DocumentParseError(ArangoClientError):
    """Failed to parse document input."""
