import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.bots.ui.templates import BaseTemplate, ChooseLanguageData
from tase.telegram.update_handlers.base import BaseHandler
from tase.utils import languages_object


class LanguageCommand(BaseCommand):
    """
    Ask users to choose a language among a menu shows a list of available languages.
    """

    command_type: BotCommandType = Field(default=BotCommandType.LANGUAGE)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        data = ChooseLanguageData(
            name=from_user.first_name or from_user.last_name,
            lang_code=from_user.chosen_language_code,
        )

        client.send_message(
            chat_id=from_user.user_id,
            text=BaseTemplate.registry.choose_language_template.render(data),
            reply_markup=languages_object.get_choose_language_markup(),
            parse_mode=ParseMode.HTML,
        )
