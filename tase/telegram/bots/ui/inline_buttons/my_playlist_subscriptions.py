from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType, ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import PlaylistItemInfo, CreateNewPublicPlaylistItemInfo


class MyPlaylistSubscriptionsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.MY_PLAYLIST_SUBSCRIPTIONS

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"${inline_command} "

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return MyPlaylistSubscriptionsButtonData()


class MyPlaylistSubscriptionsInlineButton(InlineButton):
    __type__ = InlineButtonType.MY_PLAYLIST_SUBSCRIPTIONS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "my_sub"
    __switch_inline_query_aliases__ = []

    __valid_inline_items__ = [
        InlineItemType.PLAYLIST,
        InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST,
    ]

    s_my_playlists = _trans("Playlist subscriptions")
    text = f"{s_my_playlists} | {emoji._bell}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=MyPlaylistSubscriptionsButtonData.generate_data(cls.switch_inline_query()),
            lang_code=lang_code,
        )

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        inline_button_data: Optional[MyPlaylistSubscriptionsButtonData] = None,
    ):
        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)
        playlists = await handler.db.graph.get_user_subscribed_playlists(
            from_user,
            offset=result.from_,
        )

        user_playlist_count = await handler.db.graph.get_user_playlists_count(from_user)

        if result.is_first_page() and chat_type == ChatType.BOT and user_playlist_count < 15:
            # a total number of 10 private playlists is allowed for each user (favorite playlist excluded)
            from tase.telegram.bots.ui.inline_items import CreateNewPublicPlaylistItem

            result.add_item(
                CreateNewPublicPlaylistItem.get_item(
                    from_user,
                    telegram_inline_query,
                ),
                count=False,
            )

        from tase.telegram.bots.ui.inline_items import PlaylistItem

        for playlist in playlists:
            result.add_item(
                PlaylistItem.get_item(
                    playlist,
                    from_user,
                    telegram_inline_query,
                    view_playlist=True,
                )
            )

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: MyPlaylistSubscriptionsButtonData,
        inline_item_info: Union[PlaylistItemInfo, CreateNewPublicPlaylistItemInfo],
    ):
        if inline_item_info.type == InlineItemType.CREATE_NEW_PUBLIC_PLAYLIST:
            # start creating a new public playlist
            await handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PUBLIC_PLAYLIST,
            )

            await client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line\nYou can cancel anytime by sending /cancel",
            )
        else:
            # The chosen inline item is a public playlist.
            pass
