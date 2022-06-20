from .my_playlists_button import MyPlaylistsInlineButton

# from ..handlers import BaseHandler
from ...utils import emoji, _trans


class BackToPlaylistsInlineButton(MyPlaylistsInlineButton):
    name = "back_to_playlists"

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"

    switch_inline_query_current_chat = f"#my_playlists"
