from enum import Enum


class PlaylistInteractionType(Enum):
    UNKNOWN = 0

    ###################################
    # Interaction with audios
    ###################################
    DOWNLOAD_AUDIO = 1
    REDOWNLOAD_AUDIO = 2
    LIKE_AUDIO = 3
    DISLIKE_AUDIO = 4
    SHARE_AUDIO = 5
    SHARE_AUDIO_LINK = 6

    ###################################
    # Interaction with playlists
    ###################################
    DOWNLOAD_PUBLIC_PLAYLIST = 51
    SHARE_PUBLIC_PLAYLIST = 52
    REDOWNLOAD_PUBLIC_PLAYLIST = 53
