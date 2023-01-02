import pyrogram
from pydantic import Field
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup

from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.bot_commands.base_command import BaseCommand
from tase.telegram.bots.bot_commands.bot_command_type import BotCommandType
from tase.telegram.update_handlers.base import BaseHandler


class HelpCommand(BaseCommand):
    """
    Shows the help menu
    """

    command_type: BotCommandType = Field(default=BotCommandType.HELP)
    command_description = "Show help menu"

    async def command_function(
        self,
        client: pyrogram.Client,
        message: pyrogram.types.Message,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        from_callback_query: bool,
    ) -> None:
        from tase.telegram.bots.ui.inline_buttons import (
            AdvertisementInlineButton,
            BackInlineButton,
            DownloadHistoryInlineButton,
            HelpCatalogInlineButton,
            MyPlaylistsInlineButton,
        )

        from tase.telegram.bots.ui.templates import BaseTemplate, HelpData

        data = HelpData(
            support_channel_username="support_channel_username",
            url1="https://github.com/appheap/TASE",
            url2="https://github.com/appheap/TASE",
            lang_code=from_user.chosen_language_code,
        )

        markup = [
            [
                DownloadHistoryInlineButton.get_keyboard(lang_code=from_user.chosen_language_code),
                MyPlaylistsInlineButton.get_keyboard(lang_code=from_user.chosen_language_code),
            ],
            [
                BackInlineButton.get_keyboard(lang_code=from_user.chosen_language_code),
            ],
            [
                AdvertisementInlineButton.get_keyboard(url=None, lang_code=from_user.chosen_language_code),
                HelpCatalogInlineButton.get_keyboard(lang_code=from_user.chosen_language_code),
            ],
        ]

        await client.send_message(
            chat_id=message.from_user.id,
            text=BaseTemplate.registry.help_template.render(data),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(markup),
        )
