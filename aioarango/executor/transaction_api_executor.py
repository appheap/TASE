from aioarango.connection import Connection
from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor


class TransactionAPIExecutor(BaseAPIExecutor):
    """Executes transaction API requests."""

    def __init__(
        self,
        connection: Connection,
    ):
        self.connection = connection
        self.context = APIContextType.TRANSACTION
