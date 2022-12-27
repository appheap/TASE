from typing import Match, Optional, Union

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType, ChatType
from tase.my_logger import logger
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from ..base import InlineButton, InlineButtonType, ButtonActionType, InlineItemInfo


class MyPlaylistSubscriptionsInlineButton(InlineButton):
    type = InlineButtonType.MY_PLAYLIST_SUBSCRIPTIONS
    action = ButtonActionType.CURRENT_CHAT_INLINE

    s_my_playlists = _trans("Public Playlists")
    text = f"{s_my_playlists} | {emoji._bell}"

    async def on_inline_query(
        self,
        handler: BaseHandler,
        result: CustomInlineQueryResult,
        from_user: graph_models.vertices.User,
        client: pyrogram.Client,
        telegram_inline_query: pyrogram.types.InlineQuery,
        query_date: int,
        reg: Optional[Match] = None,
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
        reg: Match,
    ):
        from tase.telegram.bots.ui.inline_items.item_info import PlaylistItemInfo, CreateNewPublicPlaylistItemInfo

        inline_item_info: Union[PlaylistItemInfo, CreateNewPublicPlaylistItemInfo, None] = InlineItemInfo.get_info(telegram_chosen_inline_result.result_id)
        if not inline_item_info or not isinstance(inline_item_info, (PlaylistItemInfo, CreateNewPublicPlaylistItemInfo)):
            logger.error(f"`{telegram_chosen_inline_result.result_id}` is not valid.")
            return

        playlist_key = inline_item_info.playlist_key if isinstance(inline_item_info, PlaylistItemInfo) else inline_item_info.item_key

        if playlist_key in "add_a_new_public_playlist":
            # start creating a new playlist
            await handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PUBLIC_PLAYLIST,
            )

            await client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line\nYou can cancel anytime by sending /cancel",
            )
