from enum import Enum


class APIContextType(Enum):
    DEFAULT = "default"
    ASYNC = "async"
    BATCH = "batch"
    TRANSACTION = "transaction"
