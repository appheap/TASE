from enum import Enum


class InlineQueryType(Enum):
    UNKNOWN = 0

    ###################################
    # Query type for audios
    ###################################
    AUDIO_SEARCH = 1
    AUDIO_COMMAND = 2

    ###################################
    # Query type for playlists
    ###################################
    PRIVATE_PLAYLIST_COMMAND = 3

    PUBLIC_PLAYLIST_SEARCH = 4
    PUBLIC_PLAYLIST_COMMAND = 5
