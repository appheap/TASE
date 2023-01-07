from enum import Enum


class AudioInteractionType(Enum):
    UNKNOWN = 0

    DOWNLOAD_AUDIO = 1
    REDOWNLOAD_AUDIO = 2
    LIKE_AUDIO = 3
    DISLIKE_AUDIO = 4
    SHARE_AUDIO = 5
    SHARE_AUDIO_LINK = 6
