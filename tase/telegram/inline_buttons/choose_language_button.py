import pyrogram

from .inline_button import InlineButton
from ..telegram_client import TelegramClient
# from ..handlers import BaseHandler
from ...db import DatabaseClient, graph_models
from ...utils import _trans


class ChooseLanguageInlineButton(InlineButton):
    name = "choose_language"

    def on_callback_query(
        self,
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
        handler: "BaseHandler",
        db: "DatabaseClient",
        telegram_client: "TelegramClient",
        db_from_user: graph_models.vertices.User,
    ):
        controller, data = callback_query.data.split("->")
        db.update_user_chosen_language(db_from_user, data)
        text = _trans("Language change has been saved", lang_code=data)
        callback_query.answer(text, show_alert=False)
        callback_query.message.delete()
