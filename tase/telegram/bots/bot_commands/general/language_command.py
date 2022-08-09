import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.utils import languages_object
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.templates import BaseTemplate, ChooseLanguageData


class LanguageCommand(BaseCommand):
    """
    Ask users to choose a language among a menu shows a list of available languages.
    """

    command_type: BotCommandType = Field(default=BotCommandType.LANGUAGE)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:
        data = ChooseLanguageData(
            name=db_from_user.first_name or db_from_user.last_name,
            lang_code=db_from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=db_from_user.user_id,
            text=BaseTemplate.registry.choose_language_template.render(data),
            reply_markup=languages_object.get_choose_language_markup(),
            parse_mode=ParseMode.HTML,
        )
