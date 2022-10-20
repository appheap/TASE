import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButton, InlineButtonType


class ChooseLanguageInlineButton(InlineButton):
    name = "choose_language"
    type = InlineButtonType.CHOOSE_LANGUAGE
    is_inline = False

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        controller, lang_code, chat_type_value = telegram_callback_query.data.split("->")
        from_user.update_chosen_language(lang_code)
        text = _trans(
            "Language change has been saved",
            lang_code=lang_code,
        )
        telegram_callback_query.answer(
            text,
            show_alert=False,
        )
        telegram_callback_query.message.delete()
