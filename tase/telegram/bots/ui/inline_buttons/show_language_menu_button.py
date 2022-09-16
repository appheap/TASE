import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .inline_button import InlineButton


class ShowLanguageMenuInlineButton(InlineButton):
    name = "show_language_menu"

    s_language = _trans("Language")
    text = f"{s_language} | {emoji._globe_showing_Americas}"
    callback_data = "show_language_menu->show_language_menu"

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        telegram_callback_query.answer("", show_alert=False)
        telegram_callback_query.message.delete()

        bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.LANGUAGE,
        )
