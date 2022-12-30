from enum import Enum


class AudioAccessSourceType(Enum):
    UNKNOWN = 0
    AUDIO_SEARCH = 1
    DOWNLOAD_HISTORY = 2
    PRIVATE_PLAYLIST = 3
    PUBLIC_PLAYLIST = 4
