from enum import Enum


class InlineItemType(Enum):
    UNKNOWN = 0

    AUDIO_IN_NO_PLAYLIST = 1
    AUDIO = 2
    CREATE_NEW_PRIVATE_PLAYLIST = 3
    CREATE_NEW_PUBLIC_PLAYLIST = 4
    NO_DOWNLOAD = 5
    NO_PLAYLIST = 6
    NO_RESULT = 7
    PLAYLIST = 8
