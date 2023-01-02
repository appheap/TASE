from typing import List, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class BackButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.BACK

    @classmethod
    def generate_data(cls) -> Optional[str]:
        return f"{cls.get_type_value()}|"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return BackButtonData()


class BackInlineButton(InlineButton):
    __type__ = InlineButtonType.BACK
    action = ButtonActionType.CALLBACK

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"

    @classmethod
    def get_keyboard(
        cls,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=BackButtonData.generate_data(),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: BackButtonData,
    ):
        # todo: what to do when the `callback_query.message` is None?
        if telegram_callback_query.message:
            await telegram_callback_query.message.delete()
        else:
            await telegram_callback_query.answer("")
