import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType
from tase.telegram.update_handlers.base import BaseHandler


class ChooseLanguageInlineButton(InlineButton):
    type = InlineButtonType.CHOOSE_LANGUAGE
    action = ButtonActionType.CALLBACK

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        controller, lang_code, chat_type_value = telegram_callback_query.data.split("|")
        await from_user.update_chosen_language(lang_code)
        text = _trans(
            "Language change has been saved",
            lang_code=lang_code,
        )
        await telegram_callback_query.answer(
            text,
            show_alert=False,
        )
        await telegram_callback_query.message.delete()
