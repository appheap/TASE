from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class ShowLanguageMenuButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.SHOW_LANGUAGE_MENU

    @classmethod
    def generate_data(cls) -> Optional[str]:
        return f"{cls.get_type_value()}|"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 2:
            return None

        return ShowLanguageMenuButtonData()


class ShowLanguageMenuInlineButton(InlineButton):
    __type__ = InlineButtonType.SHOW_LANGUAGE_MENU
    action = ButtonActionType.CALLBACK

    s_language = _trans("Language")
    text = f"{s_language} | {emoji._globe_showing_Americas}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=ShowLanguageMenuButtonData.generate_data(),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: InlineButtonData,
    ):
        await telegram_callback_query.answer("", show_alert=False)
        await telegram_callback_query.message.delete()

        await bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.LANGUAGE,
        )
