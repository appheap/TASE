import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

# import tase
from tase.telegram.bot_commands.base_command import BaseCommand
from tase.telegram.bot_commands.bot_command_type import BotCommandType
from tase.telegram.templates import BaseTemplate, WelcomeData


class StartCommand(BaseCommand):
    """
    Shows a welcome message to new users after hitting 'start' command
    """

    command_type: BotCommandType = Field(default=BotCommandType.START)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:
        self.say_welcome(client, db_from_user, message)

        # show language choosing menu if user hasn't chosen one yet
        if db_from_user.chosen_language_code is None:
            BaseCommand.run_command(client, message, self, BotCommandType.LANGUAGE)

    def say_welcome(
        self,
        client: "pyrogram.Client",
        db_from_user: "tase.db.graph_models.vertices.User",
        message: "pyrogram.types.Message",
    ) -> None:
        """
        Shows a welcome message to the user after hitting 'start'

        :param client: Telegram client
        :param db_from_user: User Object from the graph database
        :param message: Telegram message object
        :return:
        """
        data = WelcomeData(
            name=message.from_user.first_name or message.from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=message.from_user.id,
            text=BaseTemplate.registry.welcome_template.render(data),
            parse_mode=ParseMode.HTML,
        )
