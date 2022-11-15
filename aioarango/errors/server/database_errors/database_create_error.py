from aioarango.errors.base import ArangoServerError


class DatabaseCreateError(ArangoServerError):
    """Failed to create database."""
