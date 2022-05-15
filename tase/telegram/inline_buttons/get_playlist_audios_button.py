import pyrogram

from .button import InlineButton
from ..telegram_client import TelegramClient

# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import emoji, _trans


class GetPlaylistAudioInlineButton(InlineButton):
    name = "get_playlist_audios"

    s_audios = _trans("Audios")
    text = f"{s_audios} | {emoji._headphone}"

    switch_inline_query_current_chat = f"#get_playlist_audios"

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
