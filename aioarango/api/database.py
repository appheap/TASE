from .aql import AQL
from ..api_methods import APIMethods
from ..connection import Connection
from ..executor import API_Executor


class Database:
    """Base class for Database API wrappers."""

    __slots__ = [
        "_connection",
        "_executor",
        "_api",
    ]

    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
    ):
        self._connection = connection
        self._executor = executor

        self._api = APIMethods(connection, executor)

    @property
    def aql(self) -> AQL:
        return AQL(self._connection, self._executor)
