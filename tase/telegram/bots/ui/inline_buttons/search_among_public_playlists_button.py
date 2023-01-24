import asyncio
import collections
from typing import Optional, List

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import InlineQueryType, PlaylistInteractionType
from tase.db.arangodb.helpers import PlaylistHitMetadata
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemType, InlineButtonData
from ..inline_items.item_info import PlaylistItemInfo


class SearchAmongPlaylistSubscriptionsButtonData(InlineButtonData):
    __button_type__ = InlineButtonType.SEARCH_AMONG_PUBLIC_PLAYLISTS

    query: Optional[str]

    @classmethod
    def generate_data(cls, inline_command: str) -> Optional[str]:
        return f"${inline_command} "

    @classmethod
    def __parse__(
        cls,
        data_split_lst: List[str],
    ) -> Optional[InlineButtonData]:
        return SearchAmongPlaylistSubscriptionsButtonData(query=" ".join(data_split_lst[1:]) if len(data_split_lst) > 1 else None)


class SearchAmongPublicPlaylistsInlineButton(InlineButton):
    __type__ = InlineButtonType.SEARCH_AMONG_PUBLIC_PLAYLISTS
    action = ButtonActionType.CURRENT_CHAT_INLINE
    __switch_inline_query__ = "search_sub"
    __switch_inline_query_aliases__ = [
        "sub",
    ]

    __valid_inline_items__ = [InlineItemType.PLAYLIST]

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
        es_playlist_docs = None
        hit_download_urls = None
        query_metadata = None
        search_metadata_lst = None
        hit_metadata_list = None

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
                    hit_download_urls = await handler.db.graph.generate_hit_download_urls(size=len(es_playlist_docs))
                    hit_metadata_list = collections.deque()

                    for es_playlist_doc, hit_download_url in zip(es_playlist_docs, hit_download_urls):
                        hit_metadata_list.append(
                            PlaylistHitMetadata(
                                playlist_vertex_key=es_playlist_doc.id,
                                is_public_playlist=True,
                            )
                        )

                        result.add_item(
                            PlaylistItem.get_item_from_es_doc(
                                es_playlist_doc,
                                from_user,
                                telegram_inline_query,
                                playlist_hit_download_url=hit_download_url,
                                view_playlist=True,
                            )
                        )

        if not len(result) and result.is_first_page():
            from tase.telegram.bots.ui.inline_items import NoPlaylistItem

            result.set_results([NoPlaylistItem.get_item(from_user)])

        await result.answer_query()

        if query:
            playlist_vertices = None
            if es_playlist_docs:
                playlist_vertices = await handler.db.graph.get_playlists_from_keys([es_playlist_doc.id for es_playlist_doc in es_playlist_docs])
                search_metadata_lst = [es_playlist_doc.search_metadata for es_playlist_doc in es_playlist_docs]

            await handler.db.graph.get_or_create_query(
                handler.telegram_client.telegram_id,
                from_user,
                telegram_inline_query.query,
                query_date,
                playlist_vertices,
                hit_metadata_list,
                query_metadata,
                search_metadata_lst,
                telegram_inline_query=telegram_inline_query,
                inline_query_type=InlineQueryType.PUBLIC_PLAYLIST_SEARCH,
                next_offset=result.get_next_offset(only_countable=True),
                hit_download_urls=hit_download_urls,
            )

    async def on_chosen_inline_query(
        self,
        handler: BaseHandler,
        client: pyrogram.Client,
        from_user: graph_models.vertices.User,
        telegram_chosen_inline_result: pyrogram.types.ChosenInlineResult,
        inline_button_data: SearchAmongPlaylistSubscriptionsButtonData,
        inline_item_info: PlaylistItemInfo,
    ):
        from tase.telegram.bots.ui.inline_buttons.common import update_playlist_keyboard_markup

        update_keyboard_task = asyncio.create_task(
            update_playlist_keyboard_markup(
                handler.db,
                client,
                from_user,
                telegram_chosen_inline_result,
                inline_item_info,
            )
        )

        if await handler.db.graph.get_playlist_interaction_by_user(
            from_user,
            PlaylistInteractionType.DOWNLOAD_PUBLIC_PLAYLIST,
            inline_item_info.playlist_key,
        ):
            type_ = PlaylistInteractionType.REDOWNLOAD_PUBLIC_PLAYLIST
        else:
            type_ = PlaylistInteractionType.DOWNLOAD_PUBLIC_PLAYLIST

        if not await handler.db.graph.create_playlist_interaction(
            from_user,
            handler.telegram_client.telegram_id,
            type_,
            inline_item_info.chat_type,
            inline_item_info.playlist_key,
        ):
            logger.error(f"Error in creating interaction for playlist `{inline_item_info.playlist_key}`")

        await update_keyboard_task
