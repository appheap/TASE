import pyrogram

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import _trans, emoji
from .base import InlineButton, InlineButtonType


class HomeInlineButton(InlineButton):
    name = "home"
    type = InlineButtonType.HOME

    s_home = _trans("Home")
    text = f"{s_home} | {emoji._house}"
    callback_data = "home->home"

    def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
    ):
        telegram_callback_query.answer("")

        bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.HOME,
        )
