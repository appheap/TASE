from typing import Optional, List

import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class AudioLoadingButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.AUDIO_LOADING_KEYBOARD

    hit_download_url: str

    @classmethod
    def generate_data(cls, hit_download_url: str) -> Optional[str]:
        return f"{cls.get_type_value()}|{hit_download_url}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if not len(data_split_lst) != 2:
            return None

        return AudioLoadingButtonData(hit_download_url=data_split_lst[1])


class AudioLoadingKeyboardInlineButton(InlineButton):
    __type__ = InlineButtonType.AUDIO_LOADING_KEYBOARD
    action = ButtonActionType.CALLBACK

    s_loading = _trans("Loading...")
    text = f"{s_loading}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        hit_download_url: str,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=AudioLoadingButtonData.generate_data(hit_download_url=hit_download_url),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: AudioLoadingButtonData,
    ):
        await telegram_callback_query.answer("")
