from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots import bot_commands
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class HomeButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.HOME

    @classmethod
    def generate_data(cls) -> Optional[str]:
        return f"{cls.get_type_value()}|"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return HomeButtonData()


class HomeInlineButton(InlineButton):
    __type__ = InlineButtonType.HOME
    action = ButtonActionType.CALLBACK

    s_home = _trans("Home")
    text = f"{s_home} | {emoji._house}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=HomeButtonData.generate_data(),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: HomeButtonData,
    ):
        await telegram_callback_query.answer("")

        await bot_commands.BaseCommand.run_command_from_callback_query(
            client,
            telegram_callback_query,
            handler,
            from_user,
            bot_commands.BotCommandType.HOME,
        )
