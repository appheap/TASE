from aioarango.errors.server import ArangoServerError


class DatabaseCreateError(ArangoServerError):
    """Failed to create database."""
