from enum import Enum


class BotTaskType(Enum):
    UNKNOWN = 0
    CREATE_NEW_PRIVATE_PLAYLIST = 1
    CREATE_NEW_PUBLIC_PLAYLIST = 2
    EDIT_PLAYLIST_TITLE = 3
    EDIT_PLAYLIST_DESCRIPTION = 4
    DELETE_PLAYLIST = 5
