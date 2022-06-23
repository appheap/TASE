import pyrogram

from .inline_button import InlineButton
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import _trans, emoji


class EditPlaylistInlineButton(InlineButton):
    name = "edit_playlist"

    s_edit = _trans("Edit")
    text = f"{s_edit} | {emoji._gear}"
    callback_data = "edit_playlist->edit_playlist"

    def on_callback_query(
        self,
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
    ):
        callback_query.answer("")
