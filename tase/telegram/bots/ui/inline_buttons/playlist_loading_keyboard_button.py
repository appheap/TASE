from typing import Optional, List

import pyrogram

from tase.common.utils import _trans
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class PlaylistLoadingButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.PLAYLIST_LOADING_KEYBOARD

    playlist_key: str
    is_public: bool

    @classmethod
    def generate_data(
        cls,
        playlist_key: str,
        is_public: bool,
    ) -> Optional[str]:
        return f"{cls.get_type_value()}|{playlist_key}|{int(is_public)}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 3:
            return None

        return PlaylistLoadingButtonData(
            playlist_key=data_split_lst[1],
            is_public=bool(int(data_split_lst[2])),
        )


class PlaylistLoadingKeyboardInlineButton(InlineButton):
    __type__ = InlineButtonType.PLAYLIST_LOADING_KEYBOARD
    action = ButtonActionType.CALLBACK

    s_loading = _trans("Loading...")
    text = f"{s_loading}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        playlist_key: str,
        is_public: bool,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=PlaylistLoadingButtonData.generate_data(playlist_key, is_public),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: PlaylistLoadingButtonData,
    ):
        await telegram_callback_query.answer("")
