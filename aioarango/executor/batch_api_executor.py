from aioarango.connection import Connection
from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor


class BatchAPIExecutor(BaseAPIExecutor):
    """Batch API executor"""

    def __init__(
        self,
        connection: Connection,
    ):
        self.connection = connection
        self.context = APIContextType.BATCH
