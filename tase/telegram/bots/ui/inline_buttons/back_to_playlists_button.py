from tase.common.utils import _trans, emoji
from .base import InlineButtonType
from .my_playlists_button import MyPlaylistsInlineButton


class BackToPlaylistsInlineButton(MyPlaylistsInlineButton):
    name = "back_to_playlists"
    type = InlineButtonType.BACK_TO_PLAYLISTS

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"
