from typing import Match, Optional

import pyrogram

from tase.common.utils import _trans, emoji
from tase.db.arangodb import graph as graph_models
from tase.db.arangodb.enums import ChatType
from tase.telegram.bots.inline import CustomInlineQueryResult
from tase.telegram.update_handlers.base import BaseHandler
from .base import InlineButtonType, InlineButton, ButtonActionType
from ..inline_items import PlaylistItem


class SharePlaylistInlineButton(InlineButton):
    type = InlineButtonType.SHARE_PLAYLIST
    action = ButtonActionType.OTHER_CHAT_INLINE

    s_share = _trans("Share")
    text = f"{s_share} | {emoji._link}"

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
        playlist_key = reg.group("arg1")
        playlist = await handler.db.graph.get_playlist_by_key(playlist_key)

        if result.is_first_page() and playlist and not playlist.is_soft_deleted and playlist.is_public:
            result.add_item(
                PlaylistItem.get_item(
                    playlist,
                    from_user,
                    telegram_inline_query,
                    view_playlist=True,
                ),
                count=False,
            )

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
        chat_type = ChatType(int(result_id_list[2]))
