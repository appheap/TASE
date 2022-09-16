import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .inline_button import InlineButton


class BackInlineButton(InlineButton):
    name = "back"

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"
    callback_data = "back->back"

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        # todo: what to do when the `callback_query.message` is None?
        if telegram_callback_query.message:
            telegram_callback_query.message.delete()
        else:
            telegram_callback_query.answer("")
