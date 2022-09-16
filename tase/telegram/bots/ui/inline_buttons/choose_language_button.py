import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans
from .inline_button import InlineButton


class ChooseLanguageInlineButton(InlineButton):
    name = "choose_language"

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        controller, data = telegram_callback_query.data.split("->")
        from_user.update_chosen_language(
            data,
        )
        text = _trans(
            "Language change has been saved",
            lang_code=data,
        )
        telegram_callback_query.answer(
            text,
            show_alert=False,
        )
        telegram_callback_query.message.delete()
