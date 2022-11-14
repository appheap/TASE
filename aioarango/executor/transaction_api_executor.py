from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor


class TransactionAPIExecutor(BaseAPIExecutor):
    """Executes transaction API requests."""

    context = APIContextType.TRANSACTION
