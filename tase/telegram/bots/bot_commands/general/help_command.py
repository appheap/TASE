import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.bots.ui.inline_buttons import InlineButton
from tase.telegram.bots.ui.templates import BaseTemplate, HelpData


class HelpCommand(BaseCommand):
    """
    Shows the help menu
    """

    command_type: BotCommandType = Field(default=BotCommandType.HELP)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:
        data = HelpData(
            support_channel_username="support_channel_username",
            url1="https://github.com/appheap/TASE",
            url2="https://github.com/appheap/TASE",
            lang_code=db_from_user.chosen_language_code,
        )

        markup = [
            [
                InlineButton.get_button("download_history").get_inline_keyboard_button(
                    db_from_user.chosen_language_code
                ),
                InlineButton.get_button("my_playlists").get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button("back").get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
            [
                InlineButton.get_button("advertisement").get_inline_keyboard_button(db_from_user.chosen_language_code),
                InlineButton.get_button("help_catalog").get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
        ]
        markup = InlineKeyboardMarkup(markup)

        client.send_message(
            chat_id=message.from_user.id,
            text=BaseTemplate.registry.help_template.render(data),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
