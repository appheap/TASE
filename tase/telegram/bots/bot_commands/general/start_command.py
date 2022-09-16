import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

import tase
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.bots.ui.templates import BaseTemplate, WelcomeData


class StartCommand(BaseCommand):
    """
    Shows a welcome message to new users after hitting 'start' command
    """

    command_type: BotCommandType = Field(default=BotCommandType.START)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.update_handlers.base.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
        from_callback_query: bool,
    ) -> None:
        data = WelcomeData(
            name=message.from_user.first_name or message.from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=message.from_user.id,
            text=BaseTemplate.registry.welcome_template.render(data),
            parse_mode=ParseMode.HTML,
        )

        # show language choosing menu if user hasn't chosen one yet
        if db_from_user.chosen_language_code is None:
            BaseCommand.run_command(client, message, handler, BotCommandType.LANGUAGE)
