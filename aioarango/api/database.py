from ..api_methods import APIMethods
from ..connection import Connection
from ..executor import API_Executor


class Database:
    def __init__(
        self,
        connection: Connection,
        executor: API_Executor,
    ):
        self.api = APIMethods(connection, executor)
