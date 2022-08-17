from pydantic.types import Enum


class BotTaskType(Enum):
    UNKNOWN = 0
    CREATE_NEW_PLAYLIST = 1
    EDIT_PLAYLIST_TITLE = 2
    EDIT_PLAYLIST_DESCRIPTION = 3
    DELETE_PLAYLIST = 4
