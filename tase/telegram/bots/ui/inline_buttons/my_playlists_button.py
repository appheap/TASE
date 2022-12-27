from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import BotTaskType, ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButtonType, InlineButton, ButtonActionType
from .common import populate_playlist_list
from ..inline_items import NoPlaylistItem


class MyPlaylistsInlineButton(InlineButton):
    type = InlineButtonType.MY_PLAYLISTS
    action = ButtonActionType.CURRENT_CHAT_INLINE

    s_my_playlists = _trans("My Playlists")
    text = f"{s_my_playlists} | {emoji._headphone}"

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
        if chat_type != ChatType.BOT:
            result.set_results(
                [],
                count=True,
            )
        else:
            await populate_playlist_list(
                from_user,
                handler,
                result,
                telegram_inline_query,
                view_playlist=True,
            )

            if not len(result) and result.is_first_page():
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
        result_id_list = telegram_chosen_inline_result.result_id.split("->")
        inline_query_id = result_id_list[0]
        playlist_key = result_id_list[1]
        chat_type = ChatType(int(result_id_list[2])) if len(result_id_list) == 3 else ChatType.UNKNOWN

        if playlist_key == "add_a_new_playlist":
            # start creating a new playlist
            await handler.db.document.create_bot_task(
                from_user.user_id,
                handler.telegram_client.telegram_id,
                BotTaskType.CREATE_NEW_PRIVATE_PLAYLIST,
            )

            await client.send_message(
                from_user.user_id,
                text="Enter your playlist title. Enter your playlist description in the next line\nYou can cancel anytime by sending /cancel",
            )
