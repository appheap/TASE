from enum import Enum


class InteractionType(Enum):
    UNKNOWN = 0

    DOWNLOAD = 1
    SHARE = 2
    LIKE = 3
    DISLIKE = 4
