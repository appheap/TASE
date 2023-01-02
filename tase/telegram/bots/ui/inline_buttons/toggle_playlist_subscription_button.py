from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.telegram.bots.ui.base import InlineButton, InlineButtonType, ButtonActionType, InlineButtonData
from tase.telegram.update_handlers.base import BaseHandler


class TogglePlaylistSubscriptionButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.TOGGLE_PLAYLIST_SUBSCRIPTION

    playlist_key: str
    is_subscribed: bool

    @classmethod
    def generate_data(
        cls,
        playlist_key: str,
        is_subscribed: bool,
    ) -> Optional[str]:
        return f"{cls.get_type_value()}|{playlist_key}|{int(is_subscribed)}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        if len(data_split_lst) != 3:
            return None

        return TogglePlaylistSubscriptionButtonData(
            playlist_key=data_split_lst[1],
            is_subscribed=bool(int(data_split_lst[2])),
        )


class TogglePlaylistSubscriptionInlineButton(InlineButton):
    __type__ = InlineButtonType.TOGGLE_PLAYLIST_SUBSCRIPTION
    action = ButtonActionType.CALLBACK

    s_subscribe = _trans("Subscribe")
    text = f"{s_subscribe} | {emoji._bell}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        playlist_key: str,
        is_subscribed: bool = False,  # fixme
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            callback_data=TogglePlaylistSubscriptionButtonData.generate_data(playlist_key, is_subscribed),
            lang_code=lang_code,
        )

    async def on_callback_query(
        self,
        handler: BaseHandler,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_callback_query: pyrogram.types.CallbackQuery,
        inline_button_data: TogglePlaylistSubscriptionButtonData,
    ):
        playlist = await handler.db.graph.get_playlist_by_key(inline_button_data.playlist_key)
        if not playlist:
            await telegram_callback_query.answer("Playlist is not valid anymore!")
            return

        if playlist.is_soft_deleted:
            await telegram_callback_query.answer("This playlist is deleted!")
            return

        # user who has created the playlist must not be allowed to subscribe/unsubscribe.
        if playlist.owner_user_id == from_user.user_id:
            await telegram_callback_query.answer("Operation is not allowed!")
            return

        successful, subscribed = await handler.db.graph.toggle_playlist_subscription(from_user, playlist)
        if not successful:
            await telegram_callback_query.answer("Internal error occurred!")
            return

        await telegram_callback_query.answer(_trans("Subscribed!") if subscribed else _trans("Unsubscribed!"))
