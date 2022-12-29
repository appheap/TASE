from typing import Optional, List

import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class LoadingButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.LOADING_KEYBOARD

    @classmethod
    def generate_data(cls) -> Optional[str]:
        return f"{cls.get_type_value()}|"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return LoadingButtonData()


class LoadingKeyboardInlineButton(InlineButton):
    __type__ = InlineButtonType.LOADING_KEYBOARD
    action = ButtonActionType.CALLBACK

    s_loading = _trans("Loading...")
    text = f"{s_loading}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=LoadingButtonData.generate_data(),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: LoadingButtonData,
    ):
        await telegram_callback_query.answer("")
