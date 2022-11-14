from aioarango.enums import APIContextType
from aioarango.executor import BaseAPIExecutor


class BatchAPIExecutor(BaseAPIExecutor):
    """Batch API executor"""

    context = APIContextType.BATCH
