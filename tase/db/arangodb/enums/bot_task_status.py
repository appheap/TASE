from enum import Enum


class BotTaskStatus(Enum):
    UNKNOWN = 0
    CREATED = 1
    DONE = 2
    CANCELED = 3
    DELETED = 4
    FAILED = 5
