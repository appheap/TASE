import pyrogram

from .inline_button import InlineButton
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import _trans, emoji


class HomeInlineButton(InlineButton):
    name = "home"

    s_home = _trans("Home")
    text = f"{s_home} | {emoji._house}"
    callback_data = "home->home"

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
        handler.show_home(client, db_from_user, callback_query.message)
