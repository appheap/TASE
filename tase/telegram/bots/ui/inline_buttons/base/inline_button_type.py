from enum import Enum


class InlineButtonType(Enum):
    UNKNOWN = "unknown"
    INVALID = "invalid"
    BASE = "base"

    # commands intended for testing purposes
    # DUMMY = "dummy"

    ADD_TO_PLAYLIST = "add_to_pl"
    ADVERTISEMENT = "advertisement"
    BACK = "back"
    BACK_TO_PLAYLISTS = "back_to_pl"
    CHOOSE_LANGUAGE = "choose_language"
    DELETE_PLAYLIST = "delete_playlist"
    DOWNLOAD_HISTORY = "dl_history"
    EDIT_PLAYLIST_DESCRIPTION = "edit_playlist_description"
    EDIT_PLAYLIST_TITLE = "edit_playlist_title"
    GET_PLAYLIST_AUDIOS = "get_pl"
    HELP_CATALOG = "help_catalog"
    HOME = "home"
    MY_PLAYLISTS = "my_pl"
    REMOVE_FROM_PLAYLIST = "remove_from_pl"
    SHOW_LANGUAGE_MENU = "show_language_menu"
