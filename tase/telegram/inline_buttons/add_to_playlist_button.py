import pyrogram

from .button import InlineButton
from ..telegram_client import TelegramClient

# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import emoji, _trans


class AddToPlaylistInlineButton(InlineButton):
    name = "add_to_playlist"

    s_add_to_playlist = _trans("Add To Playlist")
    text = f"{s_add_to_playlist} | {emoji._plus}"

    switch_inline_query_current_chat = f"#add_to_playlist"

    def on_inline_query(
            self,
            client: 'pyrogram.Client',
            inline_query: 'pyrogram.types.InlineQuery',
            handler: 'BaseHandler',
            db: 'DatabaseClient',
            telegram_client: 'TelegramClient',
            db_from_user: graph_models.vertices.User,
    ):
        pass
