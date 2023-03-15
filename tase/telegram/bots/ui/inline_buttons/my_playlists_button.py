from typing import Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType, ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import PlaylistItemInfo, CreateNewPrivatePlaylistItemInfo


class MyPlaylistsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.MY_PLAYLISTS

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"${inline_command} "

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return MyPlaylistsButtonData()


class MyPlaylistsInlineButton(InlineButton):
    __type__ = InlineButtonType.MY_PLAYLISTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "my_pl"
    __switch_inline_query_aliases__ = [
        "pl",
        "my_playlists",
    ]

    __valid_inline_items__ = [
        InlineItemType.PLAYLIST,
        InlineItemType.CREATE_NEW_PRIVATE_PLAYLIST,
    ]

    s_my_playlists = _trans("My Playlists")
    text = f"{s_my_playlists} | {emoji._headphone}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=MyPlaylistsButtonData.generate_data(cls.switch_inline_query()),
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
        inline_button_data: Optional[MyPlaylistsButtonData] = None,
    ):
        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)
        if chat_type != ChatType.BOT:
            result.set_results(
                [],
                count=True,
            )
        else:
            from tase.telegram.bots.ui.inline_buttons.common import populate_playlist_list

            await populate_playlist_list(
                from_user,
                handler,
                result,
                telegram_inline_query,
                view_playlist=True,
            )

            if not len(result) and result.is_first_page():
                from tase.telegram.bots.ui.inline_items import NoPlaylistItem

                result.set_results([NoPlaylistItem.get_item(from_user)])

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: MyPlaylistsButtonData,
        inline_item_info: Union[PlaylistItemInfo, CreateNewPrivatePlaylistItemInfo],
    ):
        if inline_item_info.type == InlineItemType.CREATE_NEW_PRIVATE_PLAYLIST:
            # start creating a new private playlist
            await handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PRIVATE_PLAYLIST,
            )

            await client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line\nYou can cancel anytime by sending /cancel",
            )
        else:
            # the chosen inline item is a playlist
            from tase.telegram.bots.ui.inline_buttons.common import update_playlist_keyboard_markup

            # todo: handle errors when chosen inline result does not have an inline message ID set.

            await update_playlist_keyboard_markup(
                handler.db,
                client,
                from_user,
                telegram_chosen_inline_result,
                inline_item_info,
            )
