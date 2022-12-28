from enum import Enum


class InlineButtonType(Enum):
    UNKNOWN = "unknown"
    INVALID = "invalid"
    BASE = "base"

    # commands intended for testing purposes
    # DUMMY = "dummy"

    ADD_TO_PLAYLIST = "add_to_pl"
    ADD_TO_FAVORITE_PLAYLIST = "add_to_fav_pl"
    LIKE_AUDIO = "like_audio"
    DISLIKE_AUDIO = "dislike_audio"
    ADVERTISEMENT = "advertisement"
    BACK = "back"
    BACK_TO_PLAYLISTS = "back_to_pl"
    SHOW_MORE_RESULTS = "more"
    CHOOSE_LANGUAGE = "choose_language"
    DELETE_PLAYLIST = "delete_playlist"
    DOWNLOAD_HISTORY = "downloads"
    EDIT_PLAYLIST_DESCRIPTION = "edit_playlist_description"
    EDIT_PLAYLIST_TITLE = "edit_playlist_title"
    GET_PLAYLIST_AUDIOS = "get_pl"
    HELP_CATALOG = "help_catalog"
    HOME = "home"
    TOGGLE_PLAYLIST_SETTINGS = "toggle_playlist_settings"
    TOGGLE_PLAYLIST_SUBSCRIPTION = "toggle_playlist_subscription"
    DOWNLOAD_AUDIO = "download_audio"
    LOADING_KEYBOARD = "loading_keyboard"
    MY_PLAYLISTS = "my_pl"
    MY_PLAYLIST_SUBSCRIPTIONS = "sub"
    SEARCH_AMONG_PUBLIC_PLAYLISTS = "search_sub"
    SHARE_PLAYLIST = "share_pl"
    REMOVE_FROM_PLAYLIST = "remove_from_pl"
    SHOW_LANGUAGE_MENU = "show_language_menu"
