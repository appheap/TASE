from enum import Enum


class HitType(Enum):
    UNKNOWN = 0
    SEARCH = 1
    INLINE_SEARCH = 2
    INLINE_COMMAND = 3
