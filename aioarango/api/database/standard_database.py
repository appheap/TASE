from .database import Database
from ...connection import Connection
from ...executor import DefaultAPIExecutor


class StandardDatabase(Database):
    """
    Standard database API wrapper.
    """

    def __init__(self, connection: Connection):
        super().__init__(connection, DefaultAPIExecutor(connection))

    def __repr__(self) -> str:
        return f"<StandardDatabase {self.name}>"
