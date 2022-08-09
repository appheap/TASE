import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.bots.ui.inline_buttons import InlineButton
from tase.telegram.bots.ui.templates import BaseTemplate, HomeData


class HomeCommand(BaseCommand):
    """
    Shows the Home menu
    """

    command_type: BotCommandType = Field(default=BotCommandType.HOME)

    def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: "tase.telegram.handlers.BaseHandler",
        db_from_user: "tase.db.graph_models.vertices.User",
    ) -> None:

        data = HomeData(
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
                InlineButton.get_button("show_language_menu").get_inline_keyboard_button(
                    db_from_user.chosen_language_code
                ),
            ],
            [
                InlineButton.get_button("advertisement").get_inline_keyboard_button(db_from_user.chosen_language_code),
                InlineButton.get_button("help_catalog").get_inline_keyboard_button(db_from_user.chosen_language_code),
            ],
        ]
        markup = InlineKeyboardMarkup(markup)

        chat_id = None
        if message:
            if message.chat:
                chat_id = message.chat.id
            elif message.from_user:
                chat_id = message.from_user.id
        else:
            chat_id = db_from_user.user_id

        client.send_message(
            chat_id=chat_id,
            text=BaseTemplate.registry.home_template.render(data),
            parse_mode=ParseMode.HTML,
            reply_markup=markup,
        )
