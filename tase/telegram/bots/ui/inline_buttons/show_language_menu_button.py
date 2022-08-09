import pyrogram

from tase.db import graph_models
from tase.utils import _trans, emoji
from .inline_button import InlineButton


class ShowLanguageMenuInlineButton(InlineButton):
    name = "show_language_menu"

    s_language = _trans("Language")
    text = f"{s_language} | {emoji._globe_showing_Americas}"
    callback_data = "show_language_menu->show_language_menu"

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        callback_query.answer("", show_alert=False)
        callback_query.message.delete()
        handler.choose_language(client, db_from_user)
