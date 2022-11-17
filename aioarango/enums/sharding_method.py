from enum import Enum


class ShardingMethod(Enum):
    EMPTY = ""
    FLEXIBLE = "flexible"
    SINGLE = "single"
