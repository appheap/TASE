import pyrogram

from .inline_button import InlineButton
from tase.db import graph_models
from tase.utils import _trans


class ChooseLanguageInlineButton(InlineButton):
    name = "choose_language"

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        controller, data = callback_query.data.split("->")
        handler.db.update_user_chosen_language(
            db_from_user,
            data,
        )
        text = _trans(
            "Language change has been saved",
            lang_code=data,
        )
        callback_query.answer(
            text,
            show_alert=False,
        )
        callback_query.message.delete()
