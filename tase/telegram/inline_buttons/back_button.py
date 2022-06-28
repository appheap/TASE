import pyrogram

from .inline_button import InlineButton
from ...db import graph_models
from ...utils import _trans, emoji


class BackInlineButton(InlineButton):
    name = "back"

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"
    callback_data = "back->back"

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        # todo: what to do when the `callback_query.message` is None?
        if callback_query.message:
            callback_query.message.delete()
        else:
            callback_query.answer("")
