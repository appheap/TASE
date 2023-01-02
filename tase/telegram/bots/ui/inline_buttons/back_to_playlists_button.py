from typing import Optional, List, Union

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.update_handlers.base import BaseHandler
from .my_playlists_button import MyPlaylistsInlineButton
from ..base import InlineButtonType, ButtonActionType, InlineButtonData, InlineItemType
from ..inline_items.item_info import PlaylistItemInfo, CreateNewPrivatePlaylistItemInfo
from ...inline import CustomInlineQueryResult


class BackToPlaylistsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.BACK_TO_PLAYLISTS

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"#{inline_command}"

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return BackToPlaylistsButtonData()


class BackToPlaylistsInlineButton(MyPlaylistsInlineButton):
    __type__ = InlineButtonType.BACK_TO_PLAYLISTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "back_to_pl"

    __valid_inline_items__ = [
        InlineItemType.PLAYLIST,
        InlineItemType.CREATE_NEW_PRIVATE_PLAYLIST,
    ]

    s_back = _trans("Back")
    text = f"{s_back} | {emoji._BACK_arrow}"

    @classmethod
    def get_keyboard(
        cls,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=BackToPlaylistsButtonData.generate_data(cls.switch_inline_query()),
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
        inline_button_data: Optional[InlineButtonData] = None,
    ):
        chat_type = ChatType.parse_from_pyrogram(telegram_inline_query.chat_type)
        if chat_type != ChatType.BOT:
            result.set_results(
                [],
                count=True,
            )
        else:
            await MyPlaylistsInlineButton.on_inline_query(
                self,
                handler,
                result,
                from_user,
                client,
                telegram_inline_query,
                query_date,
                inline_button_data,
            )

        await result.answer_query()

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: InlineButtonData,
        inline_item_info: Union[PlaylistItemInfo, CreateNewPrivatePlaylistItemInfo],
    ):
        await MyPlaylistsInlineButton.on_chosen_inline_query(
            self,
            handler,
            client,
            from_user,
            telegram_chosen_inline_result,
            inline_button_data,
            inline_item_info,
        )
