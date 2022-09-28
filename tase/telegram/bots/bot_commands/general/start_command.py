import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.bots.ui.templates import BaseTemplate, WelcomeData
from tase.telegram.update_handlers.base import BaseHandler


class StartCommand(BaseCommand):
    """
    Shows a welcome message to new users after hitting 'start' command
    """

    command_type: BotCommandType = Field(default=BotCommandType.START)
    command_description = "Start the bot"

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        if len(message.command) == 1:
            data = WelcomeData(
                name=message.from_user.first_name or message.from_user.last_name,
                lang_code=from_user.chosen_language_code,
            )

            client.send_message(
                chat_id=message.from_user.id,
                text=BaseTemplate.registry.welcome_template.render(data),
                parse_mode=ParseMode.HTML,
            )
        elif len(message.command) == 2:
            arg = message.command[1]
            from_user = handler.db.graph.get_interacted_user(message.from_user)
            if "dl_" in arg:
                handler.download_audio(
                    client,
                    from_user,
                    arg,
                    message,
                )
        else:
            pass

        # show language choosing menu if user hasn't chosen one yet
        if from_user.chosen_language_code is None:
            BaseCommand.run_command(client, message, handler, BotCommandType.LANGUAGE)
