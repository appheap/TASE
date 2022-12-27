import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType
from tase.telegram.update_handlers.base import BaseHandler


class HomeInlineButton(InlineButton):
    type = InlineButtonType.HOME
    action = ButtonActionType.CALLBACK

    s_home = _trans("Home")
    text = f"{s_home} | {emoji._house}"

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        await telegram_callback_query.answer("")

        await bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.HOME,
        )
