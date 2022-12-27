import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType
from tase.telegram.update_handlers.base import BaseHandler


class ShowLanguageMenuInlineButton(InlineButton):
    type = InlineButtonType.SHOW_LANGUAGE_MENU
    action = ButtonActionType.CALLBACK

    s_language = _trans("Language")
    text = f"{s_language} | {emoji._globe_showing_Americas}"

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        await telegram_callback_query.answer("", show_alert=False)
        await telegram_callback_query.message.delete()

        await bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.LANGUAGE,
        )
