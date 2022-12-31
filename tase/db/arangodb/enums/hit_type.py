from enum import Enum


class HitType(Enum):
    UNKNOWN = 0

    ###################################
    # HIT type for audios
    ###################################
    NON_INLINE_AUDIO_SEARCH = 1
    INLINE_AUDIO_SEARCH = 2
    INLINE_AUDIO_COMMAND = 3

    ###################################
    # HIT type for playlists
    ###################################
    INLINE_PRIVATE_PLAYLIST_COMMAND = 4

    INLINE_PUBLIC_PLAYLIST_SEARCH = 5
    INLINE_PUBLIC_PLAYLIST_COMMAND = 6
