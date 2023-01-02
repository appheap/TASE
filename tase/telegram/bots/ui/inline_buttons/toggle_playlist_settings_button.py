from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData


class TogglePlaylistVisibilityButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.TOGGLE_PLAYLIST_SETTINGS

    playlist_key: str
    is_settings_visible: bool

    @classmethod
    def generate_data(
        cls,
        playlist_key: str,
        is_settings_visible: bool,
    ) -> Optional[str]:
        return f"{cls.get_type_value()}|{playlist_key}|{int(is_settings_visible)}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 3:
            return None

        return TogglePlaylistVisibilityButtonData(
            playlist_key=data_split_lst[1],
            is_settings_visible=bool(int(data_split_lst[2])),
        )


class TogglePlaylistSettingsInlineButton(InlineButton):
    __type__ = InlineButtonType.TOGGLE_PLAYLIST_SETTINGS
    action = ButtonActionType.CALLBACK

    s_settings = _trans("Settings")
    text = f"{s_settings} | {emoji._gear}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        playlist_key: str,
        is_settings_visible: bool,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=TogglePlaylistVisibilityButtonData.generate_data(playlist_key, is_settings_visible),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: TogglePlaylistVisibilityButtonData,
    ):
        playlist_key = inline_button_data.playlist_key
        is_settings_visible = inline_button_data.is_settings_visible

        playlist = await handler.db.graph.get_user_playlist_by_key(
            from_user,
            playlist_key,
        )
        if not playlist:
            await telegram_callback_query.answer("Playlist is not valid!")
            return

        if playlist.is_soft_deleted:
            await telegram_callback_query.answer("This playlist is deleted!")
            return

        from tase.telegram.bots.ui.inline_buttons.common import get_playlist_markup_keyboard

        reply_markup = get_playlist_markup_keyboard(
            playlist,
            from_user,
            ChatType.BOT,
            is_settings_visible=not is_settings_visible,
        )

        if reply_markup:
            await client.edit_inline_reply_markup(telegram_callback_query.inline_message_id, reply_markup)

        await telegram_callback_query.answer("")
