from typing import Match, Optional, Union, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemInfo, InlineItemType, InlineButtonData


class SearchAmongPlaylistSubscriptionsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.SEARCH_AMONG_PUBLIC_PLAYLISTS

    query: Optional[str]

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"#{inline_command} "

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return SearchAmongPlaylistSubscriptionsButtonData(query=data_split_lst[1] if len(data_split_lst) > 1 else None)


class SearchAmongPublicPlaylistsInlineButton(InlineButton):
    __type__ = InlineButtonType.SEARCH_AMONG_PUBLIC_PLAYLISTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "search_sub"

    s_search_public_playlists = _trans("Search Public Playlists")
    text = f"{s_search_public_playlists} | {emoji._search_emoji}"

    @classmethod
    def get_keyboard(
        cls,
        *,
        lang_code: Optional[str] = "en",
    ) -> pyrogram.types.InlineKeyboardButton:
        return cls.get_button(cls.__type__).__parse_keyboard_button__(
            switch_inline_query_current_chat=SearchAmongPlaylistSubscriptionsButtonData.generate_data(cls.switch_inline_query()),
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
        inline_button_data: Optional[SearchAmongPlaylistSubscriptionsButtonData] = None,
    ):
        query = inline_button_data.query
        if telegram_inline_query:
            from tase.telegram.bots.ui.inline_items import PlaylistItem

            size = 15

            if not query or len(query) <= 2:
                if result.is_first_page():
                    es_playlist_docs, query_metadata = await handler.db.index.get_top_playlists(
                        from_=result.from_,
                        size=size,
                    )

                    if es_playlist_docs and query_metadata:
                        result.extend_results(
                            [
                                PlaylistItem.get_item_from_es_doc(
                                    es_playlist_doc,
                                    from_user,
                                    telegram_inline_query,
                                    view_playlist=True,
                                )
                                for es_playlist_doc in es_playlist_docs
                            ]
                        )

            else:
                es_playlist_docs, query_metadata = await handler.db.index.search_playlists(
                    query,
                    from_=result.from_,
                    size=size,
                )

                if es_playlist_docs and query_metadata:
                    result.extend_results(
                        [
                            PlaylistItem.get_item_from_es_doc(
                                es_playlist_doc,
                                from_user,
                                telegram_inline_query,
                                view_playlist=True,
                            )
                            for es_playlist_doc in es_playlist_docs
                        ]
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
        inline_button_data: SearchAmongPlaylistSubscriptionsButtonData,
    ):
        from tase.telegram.bots.ui.inline_items.item_info import PlaylistItemInfo

        inline_item_info: Union[PlaylistItemInfo, None] = InlineItemInfo.get_info(telegram_chosen_inline_result.result_id)
        if not inline_item_info or inline_item_info.type != InlineItemType.PLAYLIST:
            logger.error(f"`{telegram_chosen_inline_result.result_id}` is not valid.")
            return
