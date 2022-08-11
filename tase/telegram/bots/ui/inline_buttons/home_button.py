import pyrogram

from tase.db import graph_models
from tase.telegram.bots import bot_commands
from tase.utils import _trans, emoji
from .inline_button import InlineButton


class HomeInlineButton(InlineButton):
    name = "home"

    s_home = _trans("Home")
    text = f"{s_home} | {emoji._house}"
    callback_data = "home->home"

    def on_callback_query(
        self,
        handler: "BaseHandler",
        db_from_user: "graph_models.vertices.User",
        client: "pyrogram.Client",
        callback_query: "pyrogram.types.CallbackQuery",
    ):
        callback_query.answer("")

        bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            callback_query,
            handler,
            db_from_user,
            bot_commands.BotCommandType.HOME,
        )
