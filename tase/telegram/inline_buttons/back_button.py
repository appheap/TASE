import pyrogram

from .inline_button import InlineButton
from ..telegram_client import TelegramClient

# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import _trans, emoji


class BackInlineButton(InlineButton):
    name = "back"

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"
    callback_data = "back->back"

    def on_callback_query(
        self,
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
    ):
        # todo: what to do when the `callback_query.message` is None?
        if callback_query.message:
            callback_query.message.delete()
        else:
            callback_query.answer("")
